-- -----------------------------------------------------
-- Schema treeofpeace
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS treeofpeace;
CREATE SCHEMA treeofpeace;
USE treeofpeace;

-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(20) NOT NULL UNIQUE,
  `password_hash` CHAR(64) NOT NULL,
  `email` VARCHAR(320) NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `birth_date` DATE NOT NULL, 
  `location` VARCHAR(50) NOT NULL, 
  `profile_image` VARCHAR(255),
  `role` ENUM('member','moderator','admin') NOT NULL,
  `status` ENUM('active','inactive') NOT NULL,
  PRIMARY KEY (`user_id`)
);

-- -----------------------------------------------------
-- Table `messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `messages` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
  PRIMARY KEY (`message_id`),
  CONSTRAINT `fk_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `replies`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `replies` (
  `reply_id` INT NOT NULL AUTO_INCREMENT,
  `message_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL, 
  PRIMARY KEY (`reply_id`),
  CONSTRAINT `fk_message_id`
    FOREIGN KEY (`message_id`)
    REFERENCES `messages` (`message_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_reply_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);