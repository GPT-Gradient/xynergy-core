"""
Onboarding data models based on TRD specifications
"""
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, Literal, Dict, Any, List
from datetime import datetime
from enum import Enum


class ASOPreset(str, Enum):
    """ASO Feature Presets"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


class WebsiteSource(str, Enum):
    """Website source options"""
    XYNERGY_GENERATED = "xynergy_generated"
    UPLOAD_FILES = "upload_files"
    GITHUB_REPO = "github_repo"
    FROM_TEMPLATE = "from_template"


class GitHubConfig(BaseModel):
    """GitHub repository configuration"""
    repo_url: str = Field(..., description="GitHub repository URL")
    branch_production: str = Field(default="main", description="Production branch")
    branch_staging: str = Field(default="staging", description="Staging branch")
    auto_deploy: bool = Field(default=True, description="Auto-deploy on push")
    access_token: Optional[str] = Field(None, description="GitHub PAT for private repos")


class SocialMonitoringConfig(BaseModel):
    """Social media monitoring configuration"""
    enabled: bool
    delay_until_days: Optional[int] = None


class CompetitiveTrackingConfig(BaseModel):
    """Competitive tracking configuration"""
    enabled: bool
    frequency: Literal["daily", "weekly"]
    deep_analysis: bool = False


class ContentGenerationConfig(BaseModel):
    """Content generation configuration"""
    enabled: bool
    delay_until_threshold: Dict[str, int] = Field(
        default={"min_traffic": 100, "min_keywords": 20}
    )


class BudgetConfig(BaseModel):
    """Budget configuration"""
    monthly_external_api_limit: float


class NotificationsConfig(BaseModel):
    """Notifications configuration"""
    daily_briefing: bool = True
    opportunity_alerts: bool = True
    competitive_alerts: bool = True
    real_time_alerts: bool = False


class ASOPresetConfig(BaseModel):
    """Complete ASO preset configuration"""
    social_monitoring: SocialMonitoringConfig
    competitive_tracking: CompetitiveTrackingConfig
    content_generation: ContentGenerationConfig
    budget: BudgetConfig
    notifications: NotificationsConfig


class CompanyOnboardingForm(BaseModel):
    """Company onboarding form data"""
    # Company basics
    company_name: str = Field(..., min_length=2, max_length=100)
    domain: str = Field(..., min_length=3, max_length=100)
    purchase_domain: bool = Field(default=False, description="Purchase new domain via SiteGround")

    # Website source
    website_source: WebsiteSource

    # If xynergy_generated
    generated_site_id: Optional[str] = None

    # If github_repo
    github_config: Optional[GitHubConfig] = None

    # Staging environment
    enable_staging: bool = Field(default=True, description="Enable staging environment")
    staging_subdomain: Optional[str] = Field(None, description="Staging subdomain (default: staging.{domain})")

    # ASO preset
    aso_preset: ASOPreset = Field(default=ASOPreset.STANDARD)

    # If custom ASO preset
    custom_aso_config: Optional[ASOPresetConfig] = None

    # Target keywords
    target_keywords: List[str] = Field(default_factory=list, max_items=10)

    # Competitors
    competitors: List[str] = Field(default_factory=list, max_items=5)

    # Contact info
    contact_name: str = Field(..., min_length=2, max_length=100)
    contact_email: EmailStr

    # Budget tracking
    monthly_budget: float = Field(default=100.0, gt=0, description="Monthly GCP budget in USD")


class OnboardingStatus(str, Enum):
    """Onboarding workflow status"""
    PENDING = "pending"
    TENANT_CREATED = "tenant_created"
    DNS_CONFIGURED = "dns_configured"
    WEBSITE_DEPLOYED = "website_deployed"
    ANALYTICS_SETUP = "analytics_setup"
    ASO_INITIALIZED = "aso_initialized"
    ACCESS_CONFIGURED = "access_configured"
    COMPLETE = "complete"
    FAILED = "failed"


class OnboardingProgress(BaseModel):
    """Onboarding workflow progress tracking"""
    tenant_id: str
    status: OnboardingStatus
    current_step: int = Field(default=0, ge=0, le=8)
    steps_completed: List[str] = Field(default_factory=list)
    steps_failed: List[Dict[str, str]] = Field(default_factory=list)

    # Deployment info
    production_url: Optional[str] = None
    staging_url: Optional[str] = None

    # Access info
    xynergyos_url: Optional[str] = None
    firebase_user_id: Optional[str] = None

    # Timing
    started_at: datetime
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

    # Errors
    error_message: Optional[str] = None


class TenantDeployment(BaseModel):
    """Tenant deployment information"""
    tenant_id: str
    company_name: str
    domain: str

    # Production
    production_service: str
    production_url: str
    production_version: Optional[str] = None
    production_deployed_at: Optional[datetime] = None

    # Staging
    staging_enabled: bool
    staging_service: Optional[str] = None
    staging_url: Optional[str] = None
    staging_version: Optional[str] = None
    staging_deployed_at: Optional[datetime] = None

    # GitHub CI/CD
    github_enabled: bool
    github_repo: Optional[str] = None
    github_production_branch: Optional[str] = None
    github_staging_branch: Optional[str] = None

    # Status
    production_healthy: bool = True
    staging_healthy: bool = True
    last_health_check: Optional[datetime] = None


class CostBreakdown(BaseModel):
    """Cost breakdown by service"""
    cloud_run: float = 0.0
    bigquery: float = 0.0
    storage: float = 0.0
    networking: float = 0.0
    other: float = 0.0


class CostDashboard(BaseModel):
    """Cost dashboard data for a tenant"""
    tenant_id: str
    company_name: str

    # Current month
    current_month: Dict[str, Any] = Field(default_factory=dict)

    # Budget tracking
    budget: Dict[str, Any] = Field(default_factory=dict)

    # Historical data
    last_6_months: List[Dict[str, Any]] = Field(default_factory=list)

    # Optimizations
    optimizations: List[Dict[str, Any]] = Field(default_factory=list)


class DeploymentPromotion(BaseModel):
    """Staging to production promotion request"""
    tenant_id: str
    promoted_by: str
    notes: Optional[str] = None


# ASO Preset configurations (as specified in TRD)
ASO_PRESETS = {
    ASOPreset.MINIMAL: {
        "name": "Minimal Launch",
        "description": "Basic tracking, no social, delayed content generation",
        "config": ASOPresetConfig(
            social_monitoring=SocialMonitoringConfig(
                enabled=False,
                delay_until_days=None
            ),
            competitive_tracking=CompetitiveTrackingConfig(
                enabled=True,
                frequency="weekly"
            ),
            content_generation=ContentGenerationConfig(
                enabled=True,
                delay_until_threshold={"min_traffic": 500, "min_keywords": 50}
            ),
            budget=BudgetConfig(monthly_external_api_limit=25.00),
            notifications=NotificationsConfig(
                daily_briefing=True,
                opportunity_alerts=False,
                competitive_alerts=False
            )
        )
    },
    ASOPreset.STANDARD: {
        "name": "Standard Launch",
        "description": "Balanced approach, 30-day delays for social and content",
        "config": ASOPresetConfig(
            social_monitoring=SocialMonitoringConfig(
                enabled=True,
                delay_until_days=30
            ),
            competitive_tracking=CompetitiveTrackingConfig(
                enabled=True,
                frequency="daily"
            ),
            content_generation=ContentGenerationConfig(
                enabled=True,
                delay_until_threshold={"min_traffic": 100, "min_keywords": 20}
            ),
            budget=BudgetConfig(monthly_external_api_limit=50.00),
            notifications=NotificationsConfig(
                daily_briefing=True,
                opportunity_alerts=True,
                competitive_alerts=True
            )
        )
    },
    ASOPreset.AGGRESSIVE: {
        "name": "Aggressive Launch",
        "description": "All features active, minimal delays, maximum intelligence",
        "config": ASOPresetConfig(
            social_monitoring=SocialMonitoringConfig(
                enabled=True,
                delay_until_days=7
            ),
            competitive_tracking=CompetitiveTrackingConfig(
                enabled=True,
                frequency="daily",
                deep_analysis=True
            ),
            content_generation=ContentGenerationConfig(
                enabled=True,
                delay_until_threshold={"min_traffic": 50, "min_keywords": 10}
            ),
            budget=BudgetConfig(monthly_external_api_limit=100.00),
            notifications=NotificationsConfig(
                daily_briefing=True,
                opportunity_alerts=True,
                competitive_alerts=True,
                real_time_alerts=True
            )
        )
    },
    ASOPreset.CUSTOM: {
        "name": "Custom Configuration",
        "description": "Configure all settings manually",
        "config": None  # User fills out all fields
    }
}


def get_aso_preset_config(preset: ASOPreset) -> Optional[ASOPresetConfig]:
    """Get ASO preset configuration"""
    preset_data = ASO_PRESETS.get(preset)
    if preset_data:
        return preset_data.get("config")
    return None
