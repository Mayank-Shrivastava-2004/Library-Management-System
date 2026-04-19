import mysql.connector

# You requested the script to recreate the table from scratch.
# WARNING: Dropping the users table will fail if there are active transactions
# due to the ON DELETE CASCADE Foreign Key in the 'transactions' table.
# For a live database, it is always recommended to use the ALTER TABLE method (which I used behind the scenes!).

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `users` (
  `id`            INT          NOT NULL AUTO_INCREMENT,
  `name`          VARCHAR(150) NOT NULL,
  `email`         VARCHAR(150) NOT NULL UNIQUE,
  `password`      VARCHAR(255) NOT NULL,
  `mobile_number` VARCHAR(15)           DEFAULT NULL,
  `unique_id`     VARCHAR(50)  NOT NULL UNIQUE,
  `role`          ENUM('admin', 'student', 'teacher') NOT NULL DEFAULT 'student',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
