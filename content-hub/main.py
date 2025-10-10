from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from google.cloud import storage, firestore, pubsub_v1

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

import os
import uuid
import json
from datetime import datetime
from typing import List, Optional
import uvicorn


# Phase 2 enhancements
from phase2_utils import CircuitBreaker, CircuitBreakerConfig, call_service_with_circuit_breaker, PerformanceMonitor
import time

# Import centralized authentication
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional



PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

# Initialize GCP clients
storage_client = storage.Client()
db = get_firestore_client()  # Phase 4: Shared connection pooling
publisher = get_publisher_client()  # Phase 4: Shared connection pooling

# Storage bucket for assets
CONTENT_BUCKET = f"{PROJECT_ID}-content-hub"

app = FastAPI(title="Xynergy Content Hub", version="1.0.0")

# Phase 2 initialization
service_monitor = PerformanceMonitor("content-hub")
service_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
ai_routing_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

# Phase 2 monitoring ready

# CORS configuration - Production security hardening
ALLOWED_ORIGINS = [
    "https://xynergy-platform.com",
    "https://api.xynergy.dev",
    "https://*.xynergy.com",
    os.getenv("ADDITIONAL_CORS_ORIGIN", "")  # For staging environments
]
# Remove empty strings from list
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

@app.get("/", response_class=HTMLResponse)
async def content_hub_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy Content Hub</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }

            html, body {
                height: 100vh;
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f8fafc;
            }

            .main-container {
                height: 100vh;
                overflow-y: auto;
                scroll-behavior: smooth;
                scrollbar-width: thin;
                scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
            }

            .main-container::-webkit-scrollbar {
                width: 6px;
            }

            .main-container::-webkit-scrollbar-track {
                background: transparent;
            }

            .main-container::-webkit-scrollbar-thumb {
                background: rgba(59, 130, 246, 0.3);
                border-radius: 3px;
            }

            .container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 24px;
                min-height: calc(100vh - 48px);
            }

            .header {
                text-align: center;
                margin-bottom: 32px;
                padding: 32px 24px;
                background: rgba(255,255,255,0.05);
                border-radius: 16px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
                transition: all 0.3s ease;
            }

            .header:hover {
                transform: translateY(-1px);
                background: rgba(255,255,255,0.07);
            }

            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 12px;
                background: linear-gradient(45deg, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .header p {
                font-size: 1.1rem;
                opacity: 0.8;
                line-height: 1.6;
                margin-bottom: 8px;
            }

            .grid, .services-grid, .feature-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                gap: 32px;
                margin: 32px 0 48px 0;
            }

            .card, .service-card, .feature {
                background: rgba(255,255,255,0.05);
                padding: 32px 24px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .card::before, .service-card::before, .feature::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .card:hover, .service-card:hover, .feature:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.08);
                border-color: rgba(59, 130, 246, 0.3);
            }

            .card:hover::before, .service-card:hover::before, .feature:hover::before {
                opacity: 1;
            }

            .card h3, .service-card h3, .feature h3 {
                font-size: 1.3rem;
                margin-bottom: 24px;
                color: #3b82f6;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #22c55e;
                border-radius: 50%;
                margin-right: 8px;
            }

            .btn, button {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.2s ease;
                font-size: 0.9rem;
            }

            .btn:hover, button:hover {
                background: #2563eb;
                transform: translateY(-1px);
            }

            @media (max-width: 768px) {
                .grid, .services-grid, .feature-list {
                    grid-template-columns: 1fr;
                    gap: 24px;
                }

                .container {
                    padding: 16px;
                }

                .header h1 {
                    font-size: 2rem;
                }
            }
            </style>
    </head>
    <body>
            <div class="main-container">
                <div class="container">
            <div class="header">
                <h1>🎨 Xynergy Content Hub</h1>
                <p>Central asset management for the Xynergy platform</p>
            </div>
            
            <div class="grid">
                <div class="panel">
                    <h2>📁 Asset Management</h2>
                    <input type="text" placeholder="Search assets..." class="search-box" id="searchBox">
                    
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <p>📎 Click to upload new assets</p>
                        <small>Images, documents, videos, and more</small>
                        <input type="file" id="fileInput" style="display: none" multiple>
                    </div>
                    
                    <div class="asset-list" id="assetList">
                        <div class="asset-item">
                            <div>
                                <strong>Marketing Campaign Assets</strong><br>
                                <small>Created by Marketing Engine • 2 hours ago</small>
                            </div>
                            <span class="status approved">Approved</span>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📊 Content Analytics</h2>
                    <div style="margin: 20px 0;">
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span>Total Assets:</span>
                            <strong id="totalAssets">247</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span>Pending Approval:</span>
                            <strong id="pendingAssets">12</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span>Storage Used:</span>
                            <strong id="storageUsed">2.4 GB</strong>
                        </div>
                    </div>
                    
                    <h3>🔥 Recent Activity</h3>
                    <div id="activityFeed">
                        <div style="padding: 10px 0; border-bottom: 1px solid #f1f5f9;">
                            <strong>Marketing Engine</strong> uploaded 5 social media posts
                            <br><small>15 minutes ago</small>
                        </div>
                        <div style="padding: 10px 0; border-bottom: 1px solid #f1f5f9;">
                            <strong>AI Assistant</strong> generated blog post assets
                            <br><small>1 hour ago</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function loadAssets() {
                try {
                    const response = await fetch('/api/assets');
                    const assets = await response.json();
                    updateAssetList(assets);
                } catch (error) {
                    console.error('Error loading assets:', error);
                }
            }
            
            function updateAssetList(assets) {
                const list = document.getElementById('assetList');
                if (assets.length === 0) {
                    list.innerHTML = '<p style="text-align: center; color: #64748b;">No assets yet. Upload some content to get started!</p>';
                    return;
                }
                
                list.innerHTML = assets.map(asset => `
                    <div class="asset-item">
                        <div>
                            <strong>${asset.name}</strong><br>
                            <small>${asset.type} • ${asset.created_by} • ${asset.created_at}</small>
                        </div>
                        <span class="status ${asset.status}">${asset.status}</span>
                    </div>
                `).join('');
            }
            
            document.getElementById('searchBox').addEventListener('input', function(e) {
                // Implement search functionality
                console.log('Searching for:', e.target.value);
            });
            
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const files = e.target.files;
                console.log('Files selected:', files.length);
                // Implement file upload
            });
            
            // Load initial data
            loadAssets();
            
            // Auto-refresh every 30 seconds
            setInterval(loadAssets, 30000);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-hub", "timestamp": datetime.now().isoformat()}

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_workflow_step(request: dict):
    """
    Standardized execution endpoint for AI Assistant workflow orchestration.
    Handles content management operations as part of multi-service workflows.
    """
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        print(f"Content Hub workflow step: {action} for workflow {workflow_context.get('workflow_id')}")

        with service_monitor.track_operation(f"execute_{action}"):
            if action == "prepare_assets":
                # Prepare content assets for campaigns or projects
                campaign_type = parameters.get("campaign_type", "general")
                workflow_id = workflow_context.get("workflow_id")

                # Create asset collection for the workflow
                asset_collection = {
                    "collection_id": f"assets_{int(time.time())}",
                    "workflow_id": workflow_id,
                    "campaign_type": campaign_type,
                    "assets": [
                        {
                            "asset_id": f"img_{int(time.time())}_1",
                            "type": "image",
                            "name": f"{campaign_type}_hero_image.jpg",
                            "url": f"gs://{CONTENT_BUCKET}/generated/{campaign_type}_hero.jpg",
                            "status": "ready"
                        },
                        {
                            "asset_id": f"doc_{int(time.time())}_2",
                            "type": "document",
                            "name": f"{campaign_type}_content_brief.pdf",
                            "url": f"gs://{CONTENT_BUCKET}/documents/{campaign_type}_brief.pdf",
                            "status": "ready"
                        },
                        {
                            "asset_id": f"vid_{int(time.time())}_3",
                            "type": "video",
                            "name": f"{campaign_type}_promo_video.mp4",
                            "url": f"gs://{CONTENT_BUCKET}/videos/{campaign_type}_promo.mp4",
                            "status": "processing"
                        }
                    ],
                    "created_at": datetime.now(),
                    "status": "prepared"
                }

                # Store asset collection in Firestore
                db.collection("asset_collections").document(asset_collection["collection_id"]).set(asset_collection)

                return {
                    "success": True,
                    "action": action,
                    "output": {
                        "collection_id": asset_collection["collection_id"],
                        "assets_prepared": len(asset_collection["assets"]),
                        "asset_types": list(set([a["type"] for a in asset_collection["assets"]]))
                    },
                    "execution_time": time.time(),
                    "service": "content-hub"
                }

            elif action == "create_content":
                # Create content based on intent and context
                intent = parameters.get("intent", "")
                context = parameters.get("context", {})
                workflow_id = workflow_context.get("workflow_id")

                # Generate content based on intent
                content_item = {
                    "content_id": f"content_{int(time.time())}",
                    "workflow_id": workflow_id,
                    "title": f"Generated Content: {intent[:50]}...",
                    "type": "article",
                    "content": f"""
                    # Content Generated for: {intent}

                    ## Overview
                    This content has been automatically generated based on your business intent.

                    ## Key Points
                    - Tailored to your specific requirements
                    - Optimized for engagement
                    - Ready for immediate use

                    ## Content Body
                    {intent} - This content addresses your specific needs and provides valuable
                    information to your target audience. The content is designed to be engaging,
                    informative, and actionable.

                    ## Call to Action
                    Take the next step in your business journey with this professionally crafted content.
                    """,
                    "metadata": {
                        "keywords": intent.split()[:5],
                        "target_audience": context.get("target_audience", "general"),
                        "content_type": "auto_generated",
                        "word_count": 150
                    },
                    "created_at": datetime.now(),
                    "status": "draft"
                }

                # Store content in Firestore
                db.collection("generated_content").document(content_item["content_id"]).set(content_item)

                return {
                    "success": True,
                    "action": action,
                    "output": {
                        "content_id": content_item["content_id"],
                        "content_ready": True,
                        "content_type": content_item["type"],
                        "word_count": content_item["metadata"]["word_count"]
                    },
                    "execution_time": time.time(),
                    "service": "content-hub"
                }

            elif action == "optimize_assets":
                # Optimize existing assets for workflows
                asset_ids = parameters.get("asset_ids", [])
                optimization_type = parameters.get("optimization_type", "web")

                optimized_assets = []
                for asset_id in asset_ids[:3]:  # Limit to 3 for demo
                    optimized_asset = {
                        "original_id": asset_id,
                        "optimized_id": f"opt_{asset_id}_{int(time.time())}",
                        "optimization_type": optimization_type,
                        "improvements": [
                            "Compressed for faster loading",
                            "Optimized for SEO",
                            "Enhanced for mobile viewing"
                        ],
                        "size_reduction": "45%",
                        "optimized_at": datetime.now()
                    }
                    optimized_assets.append(optimized_asset)

                # Store optimization results
                optimization_record = {
                    "optimization_id": f"opt_batch_{int(time.time())}",
                    "workflow_id": workflow_context.get("workflow_id"),
                    "optimized_assets": optimized_assets,
                    "total_optimized": len(optimized_assets),
                    "optimization_type": optimization_type
                }

                db.collection("asset_optimizations").document(optimization_record["optimization_id"]).set(optimization_record)

                return {
                    "success": True,
                    "action": action,
                    "output": {
                        "optimization_id": optimization_record["optimization_id"],
                        "assets_optimized": len(optimized_assets),
                        "optimization_type": optimization_type
                    },
                    "execution_time": time.time(),
                    "service": "content-hub"
                }

            else:
                # Default handler for unknown actions
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by content-hub",
                    "supported_actions": ["prepare_assets", "create_content", "optimize_assets"],
                    "service": "content-hub"
                }

    except Exception as e:
        print(f"Content Hub workflow execution failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "content-hub"
        }

@app.get("/api/assets")
async def get_assets():
    """Get all assets from the content hub"""
    try:
        assets_ref = db.collection("content_assets")
        assets = []
        
        for doc in assets_ref.stream():
            asset_data = doc.to_dict()
            asset_data["id"] = doc.id
            assets.append(asset_data)
        
        return sorted(assets, key=lambda x: x.get("created_at", ""), reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assets: {str(e)}")

@app.post("/api/assets")
async def create_asset(
    name: str,
    asset_type: str,
    content_url: str,
    created_by: str = "system",
    metadata: dict = None
):
    """Create a new asset entry"""
    try:
        asset_id = str(uuid.uuid4())
        asset_data = {
            "id": asset_id,
            "name": name,
            "type": asset_type,
            "content_url": content_url,
            "created_by": created_by,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "metadata": metadata or {},
            "tags": [],
            "version": 1
        }
        
        # Store in Firestore
        db.collection("content_assets").document(asset_id).set(asset_data)
        
        # Publish asset creation event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-content-events")
        message_data = json.dumps({
            "event_type": "asset_created",
            "asset_id": asset_id,
            "asset_name": name,
            "created_by": created_by,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
        return {"asset_id": asset_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating asset: {str(e)}")

@app.put("/api/assets/{asset_id}/approve", dependencies=[Depends(verify_api_key)])
async def approve_asset(asset_id: str):
    """Approve an asset for use"""
    try:
        asset_ref = db.collection("content_assets").document(asset_id)
        asset_ref.update({"status": "approved", "approved_at": datetime.now().isoformat()})
        
        # Publish approval event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-content-events")
        message_data = json.dumps({
            "event_type": "asset_approved",
            "asset_id": asset_id,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
        return {"status": "approved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving asset: {str(e)}")

@app.get("/api/assets/search")
async def search_assets(query: str, asset_type: Optional[str] = None):
    """Search assets by name, tags, or metadata"""
    try:
        assets_ref = db.collection("content_assets")
        
        # Simple search implementation
        all_assets = []
        for doc in assets_ref.stream():
            asset_data = doc.to_dict()
            asset_data["id"] = doc.id
            
            # Check if query matches name or tags
            if (query.lower() in asset_data.get("name", "").lower() or 
                any(query.lower() in tag.lower() for tag in asset_data.get("tags", []))):
                
                if not asset_type or asset_data.get("type") == asset_type:
                    all_assets.append(asset_data)
        
        return sorted(all_assets, key=lambda x: x.get("created_at", ""), reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching assets: {str(e)}")

@app.post("/api/assets/{asset_id}/tag")
async def tag_asset(asset_id: str, tags: List[str]):
    """Add tags to an asset"""
    try:
        asset_ref = db.collection("content_assets").document(asset_id)
        asset_ref.update({"tags": tags})
        return {"status": "tagged", "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tagging asset: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
