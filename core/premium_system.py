PERSONAL = "personal"      # $12/month
    FAMILY = "family"          # $20/month
    ENTERPRISE = "enterprise"  # $50/month

class PremiumLimits:

    LIMITS = {
        "free": {
            "conversations_per_month": 999999,
            "ais_per_week": 999999,
            "collaborators_per_project": 999999,
            "storage_gb": 999999,
            "encryption_level": "high",
            "marketplace_access": True,
            "code_editor": True,
        },
        "personal": {
            "conversations_per_month": 999999,
            "ais_per_week": 999999,
            "ais_per_month": 999999,
            "collaborators_per_project": 999999,
            "storage_gb": 999999,
            "encryption_level": "high",
            "marketplace_access": True,
            "code_editor": True,
        },
        "family": {
            "conversations_per_month": 999999,
            "ais_per_week": 999999,
            "ais_per_month": 999999,
            "collaborators_per_project": 999999,
            "storage_gb": 999999,
            "encryption_level": "high",
            "marketplace_access": True,
            "code_editor": True,
            "family_members": 999999,
        },
        "enterprise": {
            "conversations_per_month": 999999,
            "ais_per_week": 999999,
            "ais_per_month": 999999,
            "collaborators_per_project": 999999,
            "storage_gb": 999999,
            "encryption_level": "high",
            "marketplace_access": True,
            "code_editor": True,
            "team_members": 999999,
        }
    }

    @staticmethod
    def get_limit(tier, feature):
        tier_str = tier.value if isinstance(tier, PremiumTier) else tier
        if tier_str in PremiumLimits.LIMITS:
            return PremiumLimits.LIMITS[tier_str].get(feature, 0)
        return 0

    @staticmethod
    def get_all_limits(tier):
        tier_str = tier.value if isinstance(tier, PremiumTier) else tier
        return PremiumLimits.LIMITS.get(tier_str, {})

class SubscriptionPlan:

    PLANS = {
        "personal": {
            "name": "Personal",
            "price": 12.00,  # USD per month
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": ["Personal use", "High encryption", "Marketplace access", "Code editor"]
        },
        "family": {
            "name": "Family",
            "price": 20.00,  # USD per month
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": ["Up to 4 family members", "High encryption", "Marketplace access", "Code editor"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 50.00,  # USD per month
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": ["Up to 50 team members", "Military encryption", "Full marketplace", "Advanced code editor", "Priority support"]
        }
    }

    @staticmethod
    def get_plan(tier):
        tier_str = tier.value if isinstance(tier, PremiumTier) else tier
        return SubscriptionPlan.PLANS.get(tier_str, None)

class UserPremium:

    def __init__(self, user_id, tier=PremiumTier.FREE, payment_method=None):
        self.user_id = user_id
        self.tier = tier
        self.payment_method = payment_method  # Will be set by payment system
        self.subscription_start = None
        self.subscription_end = None
        self.is_active = True
        self.auto_renew = True
        self.family_members = []  # For family/enterprise plans
        self.team_members = []

    def set_subscription(self, tier, days=30):
        self.tier = tier
        self.subscription_start = datetime.now()
        self.subscription_end = datetime.now() + timedelta(days=days)
        self.is_active = True

    def is_premium(self):
        if self.tier == PremiumTier.FREE:
            return False
        if not self.is_active:
            return False
        if self.subscription_end and self.subscription_end < datetime.now():
            return False
        return True

    def add_family_member(self, user_id):
        if self.tier == PremiumTier.FAMILY:
            max_members = PremiumLimits.get_limit(self.tier, "family_members")
            if len(self.family_members) < max_members:
                self.family_members.append(user_id)
                return True
        return False

    def add_team_member(self, user_id):
        if self.tier == PremiumTier.ENTERPRISE:
            max_members = PremiumLimits.get_limit(self.tier, "team_members")
            if len(self.team_members) < max_members:
                self.team_members.append(user_id)
                return True
        return False

    def get_encryption_level(self):
        return PremiumLimits.get_limit(self.tier, "encryption_level")

class UsageTracker:

    def __init__(self, user_id):
        self.user_id = user_id
        self.conversations_this_month = 0
        self.ais_this_week = 0
        self.ais_this_month = 0
        self.last_reset_date = datetime.now()

    def can_create_conversation(self, user_premium):
        limit = PremiumLimits.get_limit(user_premium.tier, "conversations_per_month")
        return self.conversations_this_month < limit

    def can_create_ai(self, user_premium):
        limit = PremiumLimits.get_limit(user_premium.tier, "ais_per_week")
        return self.ais_this_week < limit

    def increment_conversation(self):
        self.conversations_this_month += 1

    def increment_ai(self):
        self.ais_this_week += 1
        self.ais_this_month += 1

    def reset_monthly(self):
        if (datetime.now() - self.last_reset_date).days >= 30:
            self.conversations_this_month = 0
            self.ais_this_month = 0
            self.last_reset_date = datetime.now()

    def reset_weekly(self):
        if (datetime.now() - self.last_reset_date).days >= 7:
            self.ais_this_week = 0
            self.last_reset_date = datetime.now()

class PremiumManager:

    def __init__(self):
        self.user_subscriptions = {}  # user_id -> UserPremium
        self.usage_trackers = {}      # user_id -> UsageTracker

    def create_user_premium(self, user_id, tier=PremiumTier.FREE):
        user_premium = UserPremium(user_id, tier)
        self.user_subscriptions[user_id] = user_premium
        self.usage_trackers[user_id] = UsageTracker(user_id)
        return user_premium

    def upgrade_to_premium(self, user_id, tier, days=30):
        if user_id not in self.user_subscriptions:
            return False
        self.user_subscriptions[user_id].set_subscription(tier, days)
        return True

    def can_create_ai(self, user_id):
        if user_id not in self.user_subscriptions:
            return False
        user_premium = self.user_subscriptions[user_id]
        tracker = self.usage_trackers[user_id]
        tracker.reset_weekly()
        return tracker.can_create_ai(user_premium)

    def can_create_conversation(self, user_id):
        if user_id not in self.user_subscriptions:
            return False
        user_premium = self.user_subscriptions[user_id]
        tracker = self.usage_trackers[user_id]
        tracker.reset_monthly()
        return tracker.can_conversation(user_premium)

    def get_collaborator_limit(self, user_id):
        if user_id not in self.user_subscriptions:
            return 1  # Free plan default
        user_premium = self.user_subscriptions[user_id]
        return PremiumLimits.get_limit(user_premium.tier, "collaborators_per_project")

    def is_admin(self, user_id):
        return False  # Placeholder
