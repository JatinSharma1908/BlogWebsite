CREATE TABLE `users` (
  `id` SERIAL PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) UNIQUE NOT NULL,
  `password_hash` TEXT NOT NULL,
  `is_active` BOOLEAN DEFAULT true,
  `created_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `roles` (
  `id` SERIAL PRIMARY KEY,
  `name` VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE `permissions` (
  `id` SERIAL PRIMARY KEY,
  `name` VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE `role_permissions` (
  `role_id` INT,
  `permission_id` INT,
  PRIMARY KEY (`role_id`, `permission_id`)
);

CREATE TABLE `user_roles` (
  `user_id` INT,
  `role_id` INT,
  PRIMARY KEY (`user_id`, `role_id`)
);

CREATE TABLE `categories` (
  `id` SERIAL PRIMARY KEY,
  `tenant_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `slug` VARCHAR(120) NOT NULL
);

CREATE TABLE `tags` (
  `id` SERIAL PRIMARY KEY,
  `tenant_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `slug` VARCHAR(120) NOT NULL
);

CREATE TABLE `blogs` (
  `id` SERIAL PRIMARY KEY,
  `tenant_id` INT,
  `title` VARCHAR(255) NOT NULL,
  `slug` VARCHAR(300) NOT NULL,
  `excerpt` TEXT,
  `content` TEXT NOT NULL,
  `featured_image` TEXT,
  `status` VARCHAR(20) DEFAULT 'draft',
  `author_id` INT,
  `category_id` INT,
  `published_at` TIMESTAMP,
  `created_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `comments` (
  `id` SERIAL PRIMARY KEY,
  `tenant_id` INT,
  `blog_id` INT,
  `name` VARCHAR(100),
  `email` VARCHAR(150),
  `comment` TEXT NOT NULL,
  `status` VARCHAR(20) DEFAULT 'pending',
  `created_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE UNIQUE INDEX `categories_index_0` ON `categories` (`tenant_id`, `slug`);

CREATE UNIQUE INDEX `tags_index_1` ON `tags` (`tenant_id`, `slug`);

CREATE UNIQUE INDEX `blogs_index_2` ON `blogs` (`tenant_id`, `slug`);

CREATE INDEX `idx_blogs_tenant_status` ON `blogs` (`tenant_id`, `status`);

CREATE INDEX `idx_blogs_slug` ON `blogs` (`tenant_id`, `slug`);

ALTER TABLE `role_permissions` ADD FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE;

ALTER TABLE `role_permissions` ADD FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE;

ALTER TABLE `blogs` ADD FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

ALTER TABLE `blogs` ADD FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL;

ALTER TABLE `comments` ADD FOREIGN KEY (`blog_id`) REFERENCES `blogs` (`id`) ON DELETE CASCADE;

ALTER TABLE `user_roles` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `user_roles` ADD FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE;
