MARKETPLACE_TABLES = """

-- Identity Verification Table
CREATE TABLE IF NOT EXISTS user_identities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'unverified',  -- unverified, pending, verified, rejected, expired
    is_marketplace_seller BOOLEAN DEFAULT FALSE,
    stripe_identity_session_id VARCHAR(255),
    verified_at TIMESTAMP NULL,
    verification_expires_at TIMESTAMP NULL,
    risk_score INT DEFAULT 0,  -- 0-100
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX(user_id),
    INDEX(status),
    INDEX(is_marketplace_seller)
);

-- Verification Records (for audit trail)
CREATE TABLE IF NOT EXISTS identity_verification_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(255) NOT NULL,
    verification_type VARCHAR(100),  -- id_verification, address_verification, phone_verification, selfie
    status VARCHAR(50),  -- completed, failed, pending
    completed_at TIMESTAMP NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user_identities(user_id),
    INDEX(user_id),
    INDEX(verification_type),
    INDEX(status)
);

-- Marketplace Listings Table
CREATE TABLE IF NOT EXISTS marketplace_listings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ai_id VARCHAR(255) UNIQUE NOT NULL,
    creator_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description LONGTEXT,
    category VARCHAR(100) DEFAULT 'general',
    price_cents INT DEFAULT 0,  -- 0 = free/open-source
    status VARCHAR(50) DEFAULT 'draft',  -- draft, published, unlisted, removed
    rating DECIMAL(3,2) DEFAULT 0,
    downloads INT DEFAULT 0,
    requires_premium BOOLEAN DEFAULT FALSE,
    code_open_source BOOLEAN DEFAULT TRUE,  -- MUST be true for listing
    version VARCHAR(20) DEFAULT '1.0.0',
    tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY(creator_id) REFERENCES user_identities(user_id),
    INDEX(creator_id),
    INDEX(status),
    INDEX(category),
    INDEX(rating),
    FULLTEXT INDEX(title, description)
);

-- Marketplace Reviews Table
CREATE TABLE IF NOT EXISTS marketplace_reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ai_id VARCHAR(255) NOT NULL,
    reviewer_id VARCHAR(255) NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment LONGTEXT,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ai_id) REFERENCES marketplace_listings(ai_id),
    FOREIGN KEY(reviewer_id) REFERENCES user_identities(user_id),
    INDEX(ai_id),
    INDEX(reviewer_id),
    UNIQUE KEY(ai_id, reviewer_id)  -- One review per user per AI
);

-- Marketplace Purchases/Downloads Table
CREATE TABLE IF NOT EXISTS marketplace_downloads (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ai_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),  -- Stripe session ID if paid
    amount_cents INT DEFAULT 0,
    payment_status VARCHAR(50),  -- completed, pending, failed
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ai_id) REFERENCES marketplace_listings(ai_id),
    FOREIGN KEY(user_id) REFERENCES user_identities(user_id),
    INDEX(ai_id),
    INDEX(user_id),
    INDEX(downloaded_at)
);

-- Stripe Connect Accounts Table
CREATE TABLE IF NOT EXISTS stripe_connect_accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_account_id VARCHAR(255) UNIQUE,  -- Stripe Connect account ID
    charges_enabled BOOLEAN DEFAULT FALSE,
    transfers_enabled BOOLEAN DEFAULT FALSE,
    payouts_enabled BOOLEAN DEFAULT FALSE,
    requirements JSON,  -- Pending requirements from Stripe
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user_identities(user_id),
    INDEX(user_id),
    INDEX(stripe_account_id)
);

-- Platform Earnings/Transactions Table
CREATE TABLE IF NOT EXISTS marketplace_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id VARCHAR(255) UNIQUE,
    seller_id VARCHAR(255) NOT NULL,
    ai_id VARCHAR(255) NOT NULL,
    buyer_id VARCHAR(255) NOT NULL,
    stripe_charge_id VARCHAR(255),
    gross_amount_cents INT,  -- Total charged to buyer
    platform_fee_cents INT,  -- Platform takes this
    seller_payout_cents INT,  -- Seller receives this
    status VARCHAR(50),  -- completed, refunded, disputed
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payout_date TIMESTAMP NULL,
    FOREIGN KEY(seller_id) REFERENCES user_identities(user_id),
    FOREIGN KEY(ai_id) REFERENCES marketplace_listings(ai_id),
    FOREIGN KEY(buyer_id) REFERENCES user_identities(user_id),
    INDEX(seller_id),
    INDEX(buyer_id),
    INDEX(ai_id),
    INDEX(status)
);

-- Seller Ratings/Reputation Table
CREATE TABLE IF NOT EXISTS seller_reputation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    seller_id VARCHAR(255) UNIQUE NOT NULL,
    total_sales INT DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0,
    review_count INT DEFAULT 0,
    response_time_hours INT DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_suspended BOOLEAN DEFAULT FALSE,
    suspension_reason VARCHAR(255),
    total_earnings_cents INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY(seller_id) REFERENCES user_identities(user_id),
    INDEX(seller_id),
    INDEX(average_rating),
    INDEX(is_featured)
);

-- Compliance Flags Table
CREATE TABLE IF NOT EXISTS compliance_flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(255) NOT NULL,
    flag_type VARCHAR(100),  -- high_risk, suspicious_activity, aml_alert, etc
    reason VARCHAR(255),
    severity VARCHAR(50),  -- low, medium, high, critical
    reviewed BOOLEAN DEFAULT FALSE,
    reviewer_notes LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY(user_id) REFERENCES user_identities(user_id),
    INDEX(user_id),
    INDEX(flag_type),
    INDEX(reviewed)
);

if __name__ == "__main__":
    print("Marketplace & Identity Verification Database Setup")
    print("=" * 50)
    print("\nRun this SQL in your MySQL database:\n")
    print(get_setup_sql())
    print("\n" + "=" * 50)
    print("Database setup complete!")
