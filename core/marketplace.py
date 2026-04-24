PUBLISHED = "published"
    UNLISTED = "unlisted"
    REMOVED = "removed"

class AIMarketplaceItem:

    def __init__(self, ai_id, creator_id, title, description):
        self.ai_id = ai_id
        self.creator_id = creator_id
        self.title = title
        self.description = description
        self.price = 0.0  # Free by default (open-source)
        self.status = AIListing.DRAFT
        self.category = "general"
        self.tags = []
        self.rating = 0.0
        self.downloads = 0
        self.reviews = []
        self.code_open_source = True  # MUST be open-source
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.version = "1.0.0"
        self.requires_premium = False

    def publish(self):
        if not self.code_open_source:
            raise ValueError("AI code must be open-source to publish")
        self.status = AIListing.PUBLISHED
        self.updated_at = datetime.now()

    def unpublish(self):
        self.status = AIListing.UNLISTED
        self.updated_at = datetime.now()

    def add_review(self, reviewer_id, rating, comment):
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")

        review = {
            "reviewer_id": reviewer_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now()
        }
        self.reviews.append(review)
        self._update_rating()

    def _update_rating(self):
        if not self.reviews:
            self.rating = 0.0
            return

        total_rating = sum(r["rating"] for r in self.reviews)
        self.rating = total_rating / len(self.reviews)

    def increment_downloads(self):
        self.downloads += 1

class Marketplace:

    def __init__(self):
        self.listings = {}  # ai_id -> AIMarketplaceItem
        self.featured = []  # Featured AI IDs
        self.categories = [
            "general",
            "productivity",
            "creative",
            "analysis",
            "coding",
            "business",
            "education",
            "entertainment"
        ]

    def add_ai_to_marketplace(self, ai_id, creator_id, title, description):
        if ai_id in self.listings:
            raise ValueError("AI already in marketplace")

        item = AIMarketplaceItem(ai_id, creator_id, title, description)
        self.listings[ai_id] = item
        return item

    def publish_ai(self, ai_id):
        if ai_id not in self.listings:
            raise ValueError("AI not found")

        item = self.listings[ai_id]
        item.publish()
        return True

    def unpublish_ai(self, ai_id):
        if ai_id not in self.listings:
            return False

        self.listings[ai_id].unpublish()
        return True

    def search_marketplace(self, query, category=None, sort_by="rating"):
        results = []

        for ai in self.listings.values():
            if ai.status != AIListing.PUBLISHED:
                continue

            if category and ai.category != category:
                continue

            if query and query.lower() not in ai.title.lower():
                if query.lower() not in ai.description.lower():
                    continue

            results.append(ai)

        if sort_by == "rating":
            results.sort(key=lambda x: x.rating, reverse=True)
        elif sort_by == "downloads":
            results.sort(key=lambda x: x.downloads, reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda x: x.created_at, reverse=True)

        return results

    def get_featured(self):
        featured_items = []
        for ai_id in self.featured:
            if ai_id in self.listings:
                featured_items.append(self.listings[ai_id])
        return featured_items

    def get_trending(self, limit=10):
        all_ais = [
            ai for ai in self.listings.values()
            if ai.status == AIListing.PUBLISHED
        ]
        all_ais.sort(key=lambda x: x.downloads, reverse=True)
        return all_ais[:limit]

    def get_by_category(self, category):
        return self.search_marketplace("", category=category)

    def get_highest_rated(self, limit=10):
        all_ais = [
            ai for ai in self.listings.values()
            if ai.status == AIListing.PUBLISHED and ai.rating > 0
        ]
        all_ais.sort(key=lambda x: x.rating, reverse=True)
        return all_ais[:limit]

    def download_ai(self, ai_id, user_id):
        if ai_id not in self.listings:
            raise ValueError("AI not found")

        item = self.listings[ai_id]
        if item.status != AIListing.PUBLISHED:
            raise ValueError("AI not available")

        item.increment_downloads()

        return {
            "ai_id": ai_id,
            "user_id": user_id,
            "downloaded_at": datetime.now(),
            "code": self._get_ai_code(ai_id)  # Return AI code
        }

    def _get_ai_code(self, ai_id):
        return f"# AI Code for {ai_id}"

class MarketplaceReview:

    def __init__(self):
        self.reviews = {}  # ai_id -> [reviews]

    def add_review(self, ai_id, reviewer_id, rating, comment):
        if ai_id not in self.reviews:
            self.reviews[ai_id] = []

        review = {
            "reviewer_id": reviewer_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now(),
            "helpful_count": 0
        }
        self.reviews[ai_id].append(review)
        return review

    def get_reviews(self, ai_id):
        return self.reviews.get(ai_id, [])

    def get_average_rating(self, ai_id):
        reviews = self.get_reviews(ai_id)
        if not reviews:
            return 0.0

        total = sum(r["rating"] for r in reviews)
        return total / len(reviews)
