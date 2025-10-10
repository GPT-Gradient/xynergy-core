"""
Xynergy Platform SDK Usage Examples

This file demonstrates various ways to use the Xynergy Platform SDK
for building management dashboards and integrating with platform services.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from xynergy_platform_sdk import (
    XynergyPlatformSDK,
    create_xynergy_sdk,
    ServiceStatus,
    WorkflowStatus,
    CircuitBreakerState
)


class DashboardExamples:
    """Examples for building a management dashboard"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def real_time_dashboard_monitoring(self):
        """Example: Real-time dashboard with WebSocket updates"""
        print("=== Real-time Dashboard Monitoring ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            # Set up event handlers for real-time updates
            def on_workflow_update(event: Dict[str, Any]):
                if event.get("type") == "workflow_update":
                    print(f"🔄 Workflow {event['workflow_id']}: {event['status']}")

            def on_service_status(event: Dict[str, Any]):
                if event.get("type") == "service_status":
                    print(f"🔧 Service {event['service']}: {event['status']}")

            def on_performance_alert(event: Dict[str, Any]):
                if event.get("type") == "performance_alert":
                    print(f"⚠️  Performance Alert: {event['message']}")

            # Subscribe to events
            sdk.subscribe_to_events(on_workflow_update)
            sdk.subscribe_to_events(on_service_status)
            sdk.subscribe_to_events(on_performance_alert)

            # Connect to WebSocket for real-time updates
            await sdk.connect_websocket(auto_reconnect=True)

            # Initial dashboard load
            overview = await sdk.get_dashboard_overview()
            self._display_dashboard_overview(overview)

            # Keep monitoring for updates
            print("Monitoring for real-time updates... (Press Ctrl+C to stop)")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("Stopping monitoring...")

    async def platform_health_monitoring(self):
        """Example: Comprehensive platform health monitoring"""
        print("=== Platform Health Monitoring ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            # Get overall platform health
            health = await sdk.get_platform_health()
            print(f"🏥 Platform Status: {health.overall_status.value}")
            print(f"📊 Services: {health.healthy_services}/{health.total_services} healthy")

            if health.unhealthy_services:
                print(f"❌ Unhealthy services: {', '.join(health.unhealthy_services)}")

            # Check individual service health
            print("\n📋 Service Details:")
            for service_name, service_health in health.services.items():
                status_emoji = {
                    ServiceStatus.HEALTHY: "✅",
                    ServiceStatus.WARNING: "⚠️",
                    ServiceStatus.ERROR: "❌",
                    ServiceStatus.UNKNOWN: "❓"
                }[service_health.status]

                print(f"  {status_emoji} {service_name}: {service_health.status.value}")
                if service_health.response_time:
                    print(f"    Response time: {service_health.response_time:.2f}ms")
                if service_health.error_message:
                    print(f"    Error: {service_health.error_message}")

            # Check circuit breaker status
            circuit_breakers = await sdk.get_circuit_breaker_status()
            print("\n🔌 Circuit Breaker Status:")
            for service, breakers in circuit_breakers.items():
                for breaker_name, breaker_status in breakers.items():
                    state = breaker_status["state"]
                    failure_count = breaker_status["failure_count"]
                    print(f"  {service}.{breaker_name}: {state} ({failure_count} failures)")

    async def workflow_orchestration_example(self):
        """Example: Creating and monitoring workflows"""
        print("=== Workflow Orchestration Example ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            # Execute a business intent
            print("🚀 Executing business intent...")
            workflow = await sdk.execute_business_intent(
                intent="Create a comprehensive marketing campaign for sustainable fashion startup",
                context={
                    "company": "EcoFashion Co",
                    "budget": "$25,000",
                    "timeline": "Q2 2025",
                    "target_audience": "environmentally conscious millennials",
                    "preferred_channels": ["social_media", "influencer_marketing", "content_marketing"]
                }
            )

            print(f"📋 Workflow created: {workflow.workflow_id}")
            print(f"📊 Status: {workflow.status.value}")
            print(f"📈 Initial progress: {workflow.progress:.1%}")

            # Monitor workflow progress
            print("\n🔄 Monitoring workflow progress...")
            while workflow.status in [WorkflowStatus.PENDING, WorkflowStatus.EXECUTING]:
                await asyncio.sleep(5)  # Wait 5 seconds between checks

                # Get updated status
                workflow = await sdk.get_workflow_status(workflow.workflow_id)
                print(f"📊 Progress: {workflow.progress:.1%} - Status: {workflow.status.value}")

                # Show step details
                for step in workflow.steps:
                    step_emoji = {
                        WorkflowStatus.PENDING: "⏳",
                        WorkflowStatus.EXECUTING: "🔄",
                        WorkflowStatus.COMPLETED: "✅",
                        WorkflowStatus.FAILED: "❌"
                    }[step.status]
                    print(f"  {step_emoji} {step.service}.{step.action}: {step.status.value}")

            # Final results
            print(f"\n🎉 Workflow completed with status: {workflow.status.value}")
            if workflow.results:
                print("📋 Results:")
                print(json.dumps(workflow.results, indent=2))

    async def custom_workflow_creation(self):
        """Example: Creating custom workflows with dependencies"""
        print("=== Custom Workflow Creation ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            # Define workflow steps with dependencies
            workflow_steps = [
                {
                    "step_id": "market_research",
                    "service": "marketing-engine",
                    "action": "analyze_market",
                    "parameters": {
                        "business_type": "SaaS",
                        "target_market": "enterprise",
                        "geographic_regions": ["North America", "Europe"]
                    }
                },
                {
                    "step_id": "competitor_analysis",
                    "service": "competitive-analysis-service",
                    "action": "analyze_competitors",
                    "parameters": {
                        "industry": "enterprise_software",
                        "competitor_count": 10
                    },
                    "depends_on": ["market_research"]  # Wait for market research
                },
                {
                    "step_id": "content_strategy",
                    "service": "content-hub",
                    "action": "create_content_strategy",
                    "parameters": {
                        "content_types": ["blog_posts", "whitepapers", "case_studies"],
                        "frequency": "weekly"
                    },
                    "depends_on": ["market_research", "competitor_analysis"]  # Wait for both
                },
                {
                    "step_id": "campaign_execution",
                    "service": "marketing-engine",
                    "action": "execute_campaign",
                    "parameters": {
                        "channels": ["linkedin", "google_ads", "content_marketing"],
                        "budget_allocation": {"linkedin": 0.4, "google_ads": 0.3, "content": 0.3}
                    },
                    "depends_on": ["content_strategy"]  # Final step
                }
            ]

            # Create the workflow
            print("🏗️  Creating custom workflow...")
            workflow = await sdk.create_workflow(
                workflow_name="Enterprise SaaS Marketing Launch",
                steps=workflow_steps
            )

            print(f"📋 Custom workflow created: {workflow.workflow_id}")
            print(f"📊 Total steps: {len(workflow.steps)}")

            # You can now monitor this workflow like in the previous example

    async def performance_analytics_dashboard(self):
        """Example: Performance analytics and cost optimization tracking"""
        print("=== Performance Analytics Dashboard ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            # Get comprehensive performance metrics
            metrics = await sdk.get_performance_metrics()

            print("📊 Performance Metrics:")
            print(f"  ⏱️  Average Response Time: {metrics.average_response_time:.1f}ms")
            print(f"  📈 Requests per Minute: {metrics.requests_per_minute}")
            print(f"  ✅ Success Rate: {metrics.success_rate:.1%}")

            print("\n🤖 AI Routing Efficiency:")
            print(f"  🎯 Routing Efficiency: {metrics.ai_routing_efficiency}%")
            print(f"  💰 Cost Savings: {metrics.cost_savings_percentage}%")

            print("\n💲 Cost Analysis:")
            print(f"  📅 Today's Cost: ${metrics.total_cost_today:.2f}")
            print(f"  📊 Projected Monthly: ${metrics.projected_monthly_cost:.2f}")

            # Calculate potential savings
            original_cost = metrics.projected_monthly_cost / (1 - metrics.cost_savings_percentage/100)
            savings = original_cost - metrics.projected_monthly_cost
            print(f"  💎 Monthly Savings: ${savings:.2f}")

            # Get dashboard overview for additional context
            overview = await sdk.get_dashboard_overview()
            print(f"\n🏃‍♂️ Activity Summary:")
            print(f"  🔄 Active Workflows: {overview.active_workflows}")
            print(f"  ✅ Completed Today: {overview.completed_today}")

            # AI routing distribution
            ai_dist = overview.ai_routing_distribution
            print(f"\n🤖 AI Provider Distribution:")
            print(f"  🥇 Abacus AI: {ai_dist.get('abacus_percentage', 0)}%")
            print(f"  🥈 OpenAI: {ai_dist.get('openai_percentage', 0)}%")
            print(f"  🥉 Internal AI: {ai_dist.get('internal_percentage', 0)}%")

    async def service_integration_examples(self):
        """Example: Direct service integration"""
        print("=== Service Integration Examples ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            # Call marketing engine directly
            print("📢 Marketing Engine Integration:")
            try:
                campaign_result = await sdk.call_service(
                    service_name="marketing-engine",
                    endpoint="/api/generate-campaign",
                    method="POST",
                    payload={
                        "business_type": "E-commerce",
                        "target_audience": "millennials",
                        "budget_range": "$10,000-$50,000",
                        "campaign_goals": ["brand_awareness", "lead_generation"],
                        "preferred_channels": ["social_media", "google_ads"]
                    }
                )
                print(f"  ✅ Campaign ID: {campaign_result.get('campaign_id')}")
                print(f"  📝 Campaign Name: {campaign_result.get('campaign_name')}")
            except Exception as e:
                print(f"  ❌ Marketing engine error: {e}")

            # Call AI routing engine
            print("\n🤖 AI Routing Engine Integration:")
            try:
                routing_result = await sdk.execute_service_action(
                    service_name="ai-routing-engine",
                    action="route_request",
                    parameters={
                        "query": "Generate a social media strategy for sustainable fashion",
                        "context": {"user_id": "demo_user", "session_id": "demo_session"},
                        "preferred_provider": "abacus"
                    }
                )
                print(f"  ✅ Routing successful: {routing_result.get('success')}")
                print(f"  🎯 Selected Provider: {routing_result.get('output', {}).get('selected_provider')}")
            except Exception as e:
                print(f"  ❌ AI routing error: {e}")

            # Call content hub
            print("\n📝 Content Hub Integration:")
            try:
                content_result = await sdk.execute_service_action(
                    service_name="content-hub",
                    action="generate_content",
                    parameters={
                        "content_type": "blog_post",
                        "topic": "Sustainable Fashion Trends 2025",
                        "target_audience": "fashion-conscious consumers",
                        "tone": "informative_friendly"
                    }
                )
                print(f"  ✅ Content generation: {content_result.get('success')}")
                if content_result.get('output'):
                    content_id = content_result['output'].get('content_id')
                    print(f"  📄 Content ID: {content_id}")
            except Exception as e:
                print(f"  ❌ Content hub error: {e}")

    def _display_dashboard_overview(self, overview):
        """Helper method to display dashboard overview"""
        print("\n" + "="*50)
        print("📊 XYNERGY PLATFORM DASHBOARD")
        print("="*50)

        # Platform health
        health_emoji = {
            ServiceStatus.HEALTHY: "✅",
            ServiceStatus.WARNING: "⚠️",
            ServiceStatus.ERROR: "❌",
            ServiceStatus.UNKNOWN: "❓"
        }[overview.platform_health.overall_status]

        print(f"{health_emoji} Platform Status: {overview.platform_health.overall_status.value}")
        print(f"🏥 Services: {overview.platform_health.healthy_services}/{overview.platform_health.total_services}")

        # Activity metrics
        print(f"🔄 Active Workflows: {overview.active_workflows}")
        print(f"✅ Completed Today: {overview.completed_today}")

        # Performance metrics
        print(f"⏱️  Avg Response: {overview.cost_metrics.average_response_time:.1f}ms")
        print(f"📈 Requests/min: {overview.cost_metrics.requests_per_minute}")
        print(f"✅ Success Rate: {overview.cost_metrics.success_rate:.1%}")

        # Cost optimization
        print(f"💰 Cost Savings: {overview.cost_metrics.cost_savings_percentage}%")
        print(f"💲 Today's Cost: ${overview.cost_metrics.total_cost_today:.2f}")

        print("="*50)


# Error handling examples
class ErrorHandlingExamples:
    """Examples of proper error handling with the SDK"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def circuit_breaker_handling(self):
        """Example: Handling circuit breaker failures"""
        print("=== Circuit Breaker Error Handling ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            try:
                # This might fail if circuit breaker is open
                result = await sdk.execute_business_intent(
                    "Generate marketing campaign",
                    context={"service": "external_ai_heavy_load"}
                )
                print(f"✅ Success: {result.workflow_id}")

            except Exception as e:
                print(f"❌ Primary execution failed: {e}")

                # Check circuit breaker status
                breakers = await sdk.get_circuit_breaker_status()
                for service, breaker_states in breakers.items():
                    for breaker_name, state in breaker_states.items():
                        if state["state"] == "OPEN":
                            print(f"🔌 Circuit breaker OPEN: {service}.{breaker_name}")

                # Try alternative approach or graceful degradation
                print("🔄 Attempting fallback approach...")
                # Implement fallback logic here

    async def service_unavailable_handling(self):
        """Example: Handling service unavailability"""
        print("=== Service Unavailable Handling ===")

        async with XynergyPlatformSDK(self.api_key) as sdk:
            services = await sdk.get_service_registry()

            for service_name, service_health in services.items():
                if service_health.status != ServiceStatus.HEALTHY:
                    print(f"⚠️  Service {service_name} is {service_health.status.value}")

                    # Skip non-essential services or use alternatives
                    if service_name in ["marketing-engine", "content-hub"]:
                        print(f"🔄 {service_name} is critical, implementing fallback...")
                        # Implement fallback logic
                    else:
                        print(f"⏩ Skipping non-critical service {service_name}")


async def main():
    """Main example runner"""
    # Replace with your actual API key
    api_key = "your_xynergy_api_key_here"

    # Initialize examples
    dashboard_examples = DashboardExamples(api_key)
    error_examples = ErrorHandlingExamples(api_key)

    print("🚀 Xynergy Platform SDK Examples")
    print("Choose an example to run:")
    print("1. Real-time Dashboard Monitoring")
    print("2. Platform Health Monitoring")
    print("3. Workflow Orchestration")
    print("4. Custom Workflow Creation")
    print("5. Performance Analytics Dashboard")
    print("6. Service Integration Examples")
    print("7. Circuit Breaker Error Handling")
    print("8. Service Unavailable Handling")

    choice = input("Enter choice (1-8): ")

    try:
        if choice == "1":
            await dashboard_examples.real_time_dashboard_monitoring()
        elif choice == "2":
            await dashboard_examples.platform_health_monitoring()
        elif choice == "3":
            await dashboard_examples.workflow_orchestration_example()
        elif choice == "4":
            await dashboard_examples.custom_workflow_creation()
        elif choice == "5":
            await dashboard_examples.performance_analytics_dashboard()
        elif choice == "6":
            await dashboard_examples.service_integration_examples()
        elif choice == "7":
            await error_examples.circuit_breaker_handling()
        elif choice == "8":
            await error_examples.service_unavailable_handling()
        else:
            print("Invalid choice. Running platform health monitoring as default.")
            await dashboard_examples.platform_health_monitoring()

    except KeyboardInterrupt:
        print("\n👋 Example stopped by user")
    except Exception as e:
        print(f"❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())