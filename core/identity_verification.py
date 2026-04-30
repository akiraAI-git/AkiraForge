import stripe
from datetime import datetime
from enum import Enum

class VerificationStatus(Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

class VerificationType(Enum):
    ID_VERIFICATION = "id_verification"      # Government ID scan
    ADDRESS_VERIFICATION = "address_proof"    # Proof of address
    PHONE_VERIFICATION = "phone_verification" # Phone number verification
    SELFIE_VERIFICATION = "selfie"            # Liveness check

class UserIdentity:

    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email
        self.status = VerificationStatus.UNVERIFIED
        self.verified_at = None
        self.verification_expires_at = None
        self.identity_session_id = None  # Stripe Identity Session ID
        self.verifications = {
            VerificationType.ID_VERIFICATION: False,
            VerificationType.ADDRESS_VERIFICATION: False,
            VerificationType.PHONE_VERIFICATION: False,
            VerificationType.SELFIE_VERIFICATION: False,
        }
        self.risk_score = 0  # 0-100, higher = riskier
        self.is_marketplace_seller = False
        self.metadata = {}

    def mark_verified(self):
        self.status = VerificationStatus.VERIFIED
        self.verified_at = datetime.now()
        from datetime import timedelta
        self.verification_expires_at = datetime.now() + timedelta(days=365)

    def is_verified(self):
        if self.status != VerificationStatus.VERIFIED:
            return False
        if self.verification_expires_at and datetime.now() > self.verification_expires_at:
            self.status = VerificationStatus.EXPIRED
            return False
        return True

    def complete_verification_type(self, verification_type):
        self.verifications[verification_type] = True

    def all_required_verifications_complete(self):
        required = [
            VerificationType.ID_VERIFICATION,
            VerificationType.ADDRESS_VERIFICATION,
            VerificationType.SELFIE_VERIFICATION,
        ]
        return all(self.verifications[v] for v in required)

class IdentityVerificationService:

    def __init__(self, api_key=None):
        if api_key:
            stripe.api_key = api_key

    def create_verification_session(self, user_id, email, name, phone=None):
            session = stripe.identity.VerificationSession.create(
                type="document",  # Verify government-issued ID
                metadata={
                    "user_id": user_id,
                    "email": email,
                },
                options={
                    "document": {
                        "allowed_types": ["driving_license", "passport", "id_card"],
                    }
                },
            )
            return {
                "session_id": session.id,
                "client_secret": session.client_secret,
                "url": session.url,  # Hosted verification URL
                "success": True,
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def check_verification_status(self, session_id):
            return self.users[user_id]

        user = UserIdentity(user_id, email)
        self.users[user_id] = user
        return user

    def get_user_identity(self, user_id):
        return self.users.get(user_id)

    def initiate_seller_verification(self, user_id, email, name, phone=None):
        Call this after verifying the session status
        if not user:
            return False
        return user.is_verified() and user.is_marketplace_seller

    def can_accept_payment(self, user_id):
        return self.can_list_on_marketplace(user_id)

    def flag_user_for_review(self, user_id, reason):
        user = self.get_user_identity(user_id)
        if user:
            user.metadata["flagged_for_review"] = True
            user.metadata["flag_reason"] = reason
            user.metadata["flagged_at"] = datetime.now()
        return True

class ComplianceChecker:

    HIGH_RISK_COUNTRIES = ["KP", "IR", "SY"]  # Example

    @staticmethod
    def is_country_restricted(country_code):
        return country_code in ComplianceChecker.HIGH_RISK_COUNTRIES

    @staticmethod
    def calculate_risk_score(user_identity):
        score = 0

        if user_identity.verified_at:
            age_days = (datetime.now() - user_identity.verified_at).days
            if age_days < 30:
                score += 30
            elif age_days < 90:
                score += 15

        if user_identity.status == VerificationStatus.REJECTED:
            score += 40

        reject_count = user_identity.metadata.get("rejection_count", 0)
        score += reject_count * 10

        return min(score, 100)

    @staticmethod
    def should_require_additional_verification(user_identity):
        risk_score = ComplianceChecker.calculate_risk_score(user_identity)

        return risk_score > 60
