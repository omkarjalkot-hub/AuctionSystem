-- ============================================
-- SmartBid Online Auction System
-- Database Setup
-- ============================================

CREATE DATABASE IF NOT EXISTS SmartBid;

USE SmartBid;


-- ============================================
-- USERS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('User', 'Admin') NOT NULL DEFAULT 'User',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AUCTION ITEMS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS auction_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    starting_price DECIMAL(10,2) NOT NULL,
    bid_increment DECIMAL(10,2) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    image_path VARCHAR(255),
    status ENUM(
        'Scheduled',
        'Live',
        'Ended',
        'Sold',
        'Cancelled'
    ) DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- BIDS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS bids (
    bid_id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL,
    bidder_id INT NOT NULL,
    bid_amount DECIMAL(10,2) NOT NULL,
    bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- WINNERS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS winners (
    winner_id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL,
    winning_bid DECIMAL(10,2) NOT NULL,
    won_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PAYMENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    winner_id INT NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM(
        'UPI',
        'Card',
        'Net Banking'
    ) NOT NULL,
    payment_status ENUM(
        'Pending',
        'Paid',
        'Failed'
    ) DEFAULT 'Pending',
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CATEGORIES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- ============================================
-- TABLE RELATIONSHIPS
-- ============================================

ALTER TABLE auction_items
ADD CONSTRAINT fk_auction_seller
FOREIGN KEY (seller_id)
REFERENCES users(user_id);

ALTER TABLE auction_items
ADD CONSTRAINT fk_auction_category
FOREIGN KEY (category_id)
REFERENCES categories(category_id);

ALTER TABLE bids
ADD CONSTRAINT fk_bid_item
FOREIGN KEY (item_id)
REFERENCES auction_items(item_id);

ALTER TABLE bids
ADD CONSTRAINT fk_bidder
FOREIGN KEY (bidder_id)
REFERENCES users(user_id);

ALTER TABLE winners
ADD CONSTRAINT fk_winner_item
FOREIGN KEY (item_id)
REFERENCES auction_items(item_id);

ALTER TABLE winners
ADD CONSTRAINT fk_winner_user
FOREIGN KEY (user_id)
REFERENCES users(user_id);

ALTER TABLE payments
ADD CONSTRAINT fk_payment_winner
FOREIGN KEY (winner_id)
REFERENCES winners(winner_id);     

-- ============================================
-- DEFAULT AUCTION CATEGORIES
-- ============================================

INSERT IGNORE INTO categories (category_name) VALUES
('Electronics'),
('Mobiles'),
('Laptops'),
('Fashion'),
('Home & Furniture'),
('Vehicles'),
('Books'),
('Sports'),
('Collectibles'),
('Other');