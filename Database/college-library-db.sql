-- Database creation
DROP DATABASE IF EXISTS college_library_db;
CREATE DATABASE IF NOT EXISTS college_library_db;
USE college_library_db;

-- Table creation
CREATE TABLE IF NOT EXISTS users (
    login VARCHAR(40),
    password VARCHAR(30) NOT NULL,
    acess ENUM('admin', 'librarian', 'user') NOT NULL DEFAULT 'user',
    registration INT,    
    PRIMARY KEY (login)
)  DEFAULT CHARSET=UTF8;

CREATE TABLE IF NOT EXISTS courses (
    course_code INT AUTO_INCREMENT,
    course VARCHAR(40),
    course_desc TEXT,
    PRIMARY KEY (course_code)
)  DEFAULT CHARSET=UTF8;
    
CREATE TABLE IF NOT EXISTS phone_numbers (
	id_phone_numbers INT AUTO_INCREMENT NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    registration INT,
    PRIMARY KEY(id_phone_numbers)
)  DEFAULT CHARSET=UTF8;    

CREATE TABLE IF NOT EXISTS students (
    registration INT AUTO_INCREMENT,
    name VARCHAR(40) NOT NULL,
    entry_date DATE NOT NULL,
    expected_completion_date DATE NOT NULL,
    adress VARCHAR(55) NOT NULL,
    course_code INT NOT NULL,
    id_phone_numbers INT NULL,
    PRIMARY KEY (registration),
    FOREIGN KEY (course_code)
        REFERENCES courses (course_code),
	FOREIGN KEY (id_phone_numbers)
        REFERENCES phone_numbers (id_phone_numbers)
)  DEFAULT CHARSET=UTF8;
    
CREATE TABLE IF NOT EXISTS professors (
    registration INT AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL,
    hiring_date DATE NOT NULL,
    work_regime ENUM('20h', '40h', 'DE'),
    adress VARCHAR(55) NOT NULL,
    cell_phone VARCHAR(20) NOT NULL,
    course_code INT NOT NULL,    
    PRIMARY KEY (registration),
    FOREIGN KEY (course_code)
        REFERENCES courses (course_code)    
)  DEFAULT CHARSET=UTF8;
    
CREATE TABLE IF NOT EXISTS employees (
    registration INT AUTO_INCREMENT NOT NULL,
    name VARCHAR(40) NOT NULL,
    adress VARCHAR(55) NOT NULL,
    id_phone_numbers INT NULL,
    PRIMARY KEY (registration),
    FOREIGN KEY (id_phone_numbers)
        REFERENCES phone_numbers (id_phone_numbers)	
)  DEFAULT CHARSET=UTF8;
    
CREATE TABLE IF NOT EXISTS categories (
    category_code SMALLINT AUTO_INCREMENT,
    category VARCHAR(25),
    category_desc TEXT,
    PRIMARY KEY (category_code)
)  DEFAULT CHARSET=UTF8;

CREATE TABLE IF NOT EXISTS books (
    isbn_code VARCHAR(30) NOT NULL,
    title VARCHAR(100) NOT NULL,
    release_year YEAR NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    copies_available INT NOT NULL,
    category_code SMALLINT NOT NULL,
    PRIMARY KEY (isbn_code),
    FOREIGN KEY (category_code)
        REFERENCES categories (category_code)
)  DEFAULT CHARSET=UTF8;

CREATE TABLE IF NOT EXISTS authors (
    author_email VARCHAR(50) NOT NULL,
    name VARCHAR(40) NOT NULL,
    nationality VARCHAR(30) NOT NULL,
    PRIMARY KEY (author_email)
)  DEFAULT CHARSET=UTF8;
    
CREATE TABLE IF NOT EXISTS authors_write_books (
    isbn_code VARCHAR(30) NOT NULL,
    author_email VARCHAR(50) NOT NULL,
    FOREIGN KEY (isbn_code)
        REFERENCES books (isbn_code),
    FOREIGN KEY (author_email)
        REFERENCES authors (author_email)
)  DEFAULT CHARSET=UTF8;
    
CREATE TABLE IF NOT EXISTS book_borrowings (
	id_book_borrowings INT NOT NULL AUTO_INCREMENT,    
    borrow_date DATE,
    devolution_date DATE,
    isbn_code VARCHAR(30) NOT NULL,
    registration INT NULL,
    PRIMARY KEY (id_book_borrowings),
    FOREIGN KEY (isbn_code)
        REFERENCES books (isbn_code)	
)  DEFAULT CHARSET=UTF8;
    
CREATE TABLE IF NOT EXISTS book_reservations (
    reservation_date DATE,
    registration INT NOT NULL,
    isbn_code VARCHAR(30) NOT NULL,
    FOREIGN KEY (isbn_code)
        REFERENCES books (isbn_code)
)  DEFAULT CHARSET=UTF8;

-- Views
CREATE VIEW books_by_category AS
    SELECT 
        category,
        title,
        publisher,
        release_year,
        copies_available
    FROM
        books b
            INNER JOIN
        categories c ON b.category_code = c.category_code
    GROUP BY category , title , publisher , release_year , copies_available
    ORDER BY category;
    
CREATE VIEW books_by_publisher AS
    SELECT 
		publisher,
		title,
		category,
		release_year,
		copies_available
	FROM
		books b
			INNER JOIN
		categories c ON b.category_code = c.category_code
	GROUP BY publisher , title , category , release_year , copies_available
	ORDER BY publisher;
    
CREATE VIEW books_by_release AS
    SELECT 
        release_year,
        title,
        publisher,
        category,
        copies_available
    FROM
        books b
            INNER JOIN
        categories c ON b.category_code = c.category_code
    GROUP BY release_year , title , publisher , category , copies_available
    ORDER BY release_year;    

CREATE VIEW books_by_author AS
	SELECT 
		name AS author,
		title,
		publisher,
		category,
		release_year,
		copies_available
	FROM
		books b
			INNER JOIN
		categories c ON b.category_code = c.category_code
			INNER JOIN
		authors_write_books authors_books ON b.isbn_code = authors_books.isbn_code
			INNER JOIN
		authors a ON authors_books.author_email = a.author_email
	GROUP BY author , title , publisher , category , release_year , copies_available
	ORDER BY author;    

-- Function
SET GLOBAL log_bin_trust_function_creators = 1;

DELIMITER //
CREATE DEFINER = 'root'@'localhost' FUNCTION `get_user_acess` (registration INT) RETURNS VARCHAR(11)
BEGIN
    DECLARE type VARCHAR(11);
    
    IF ( (SELECT EXISTS ( SELECT registration FROM students s WHERE s.registration=registration ) ) = 1) THEN
        SET type = 'student';
    ELSEIF ( (SELECT EXISTS ( SELECT registration FROM professors p WHERE p.registration=registration ) ) = 1) THEN
        SET type = 'professor';
    ELSEIF ( (SELECT EXISTS ( SELECT registration FROM employees e WHERE e.registration=registration ) ) = 1) THEN
        SET type = 'employee';
    ELSE 
        SET type = 'none';
    END IF;
    
    RETURN type;
END; 
//
DELIMITER ;;

-- Triggers
DELIMITER //
CREATE TRIGGER `check_expected_completion_date` BEFORE INSERT ON `book_borrowings` FOR EACH ROW
IF ( (SELECT expected_completion_date FROM students s WHERE NEW.registration=s.registration) > CURDATE() ) THEN
	SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Expected completion date.';
END IF;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `check_copies_available` BEFORE INSERT ON `book_borrowings` FOR EACH ROW
IF ( (SELECT copies_available FROM books b WHERE NEW.isbn_code=b.isbn_code) = 0 ) THEN
	SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: No more copies available.';
END IF;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `reservation_date` BEFORE INSERT ON `book_reservations` FOR EACH ROW
IF ( ISNULL(NEW.reservation_date) ) THEN
	SET NEW.reservation_date=CURDATE();
END IF;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `borrow_date` BEFORE INSERT ON `book_borrowings` FOR EACH ROW
IF ( ISNULL(NEW.borrow_date) ) THEN
	SET NEW.borrow_date=CURDATE();
END IF;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `decrease_available_copies` AFTER INSERT ON `book_borrowings` FOR EACH ROW
	UPDATE books b
    SET copies_available=copies_available-1 
    WHERE NEW.isbn_code=b.isbn_code;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `delete_reservation` AFTER INSERT ON `book_borrowings` FOR EACH ROW
	DELETE FROM book_reservations r
    WHERE NEW.isbn_code=r.isbn_code;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `check_students_borrowed_books_number` BEFORE INSERT ON `book_borrowings` FOR EACH ROW
IF ( (SELECT COUNT(registration) FROM book_borrowings WHERE registration=NEW.registration) = 3 ) THEN
	SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Number of borrowings allowed per student reached (3).';
END IF;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `check_employees_borrowed_books_number` BEFORE INSERT ON `book_borrowings` FOR EACH ROW
IF ( (SELECT COUNT(registration) FROM book_borrowings WHERE registration=NEW.registration) = 4 ) THEN
	SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Number of borrowings allowed per employee reached (4).';
END IF;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER `check_professores_borrowed_books_number` BEFORE INSERT ON `book_borrowings` FOR EACH ROW
IF ( (SELECT COUNT(registration) FROM book_borrowings WHERE registration=NEW.registration) = 5 ) THEN
	SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Number of borrowings allowed per professor reached (5).';
END IF;
//
DELIMITER ;

-- Insertions
INSERT INTO users (login, password, acess) VALUES
('admin', 'admin', 'admin');

INSERT INTO users (login, password, acess) VALUES
('librarian', '1234', 'librarian');

INSERT INTO users (login, password, registration) VALUES
('lenoar_vieira', '1234', '100000'),
('alexandremmota', '1234', '100001'),
('adrianopaulo728', '1234', '100002'),
('kevin_ferreira120', '1234', '1010'),
('leandro_paulla', '1234', '1011'),
('wagnerlopes', '1234', '1012'),
('rodriguesbastiao', '1234', '1013'),
('leia_albuquerque4829', '1234', '1014'),
('lucas_limamatos223', '1234', '1000'),
('joaquim_domingos', '1234', '1001'),
('leandro_martins', '1234', '1002');

INSERT INTO courses (course, course_desc) VALUES
('Calculus 1', 'It aims to provide the student with a
Basic knowledge of the main concepts of Calculus which are: limits, derivatives and
full.'),
('Physics 1', 'Physics studies natural phenomena related to mechanics, thermology, acoustics, optics, electricity and modern physics. Physics is the science that studies nature.'),
('Discrete mathematics', 'Discrete mathematics (or, as it is sometimes called, finite mathematics or
combinatorics) is the part of mathematics devoted to the study of discrete objects and structures or
finite (discrete means that it is formed by distinct course_disconnected elements)'),
('Computer programming', 'Programming is the process of writing, testing and maintaining a computer program.'),
('Introduction to Engineering', 'Introduction to Engineering introduces fundamental engineering concepts to first-year undergraduate engineering students. ');

INSERT INTO students (registration, name, entry_date, expected_completion_date, adress, course_code) VALUES
('100000', 'Lenoar Viera Ramos', '2019-07-12', '2024-07-12', 'Java Avenue', '1'),
('100001', 'Alexandre Mota Farias', '2019-07-12', '2024-07-12', 'Java Avenue', '1'),
('100002', 'Adriano Paulo Ferreira', '2019-07-12', '2024-07-12', 'Java Avenue', '1');

INSERT INTO professors (registration, name, hiring_date, work_regime, adress, cell_phone, course_code) VALUES
('1010', 'Kevin Callom Ferreira', '2018-06-12', '20h', 'Monte Castelo', '88912345678', '1'),
('1011', 'Leandro De Paulla', '2018-06-12', '40h', 'Monte Castelo', '88917345678', '2'),
('1012','Wagner Costa Lopes', '2018-06-12', 'DE', 'Monte Castelo', '21910345678', '3'),
('1013','Rodrigues Bastião', '2018-06-12', '20h', 'Monte Castelo', '21910345878', '4'),
('1014','Léia Albuquerque', '2018-06-12', '40h', 'Monte Castelo', '21910342978', '5');

INSERT INTO employees (registration, name, adress) VALUES
('1000', 'Lucas Lima Matos', 'Álvaro Machado'),
('1001','Joaquim Domingos Silva', 'Joaquim Dantes'),
('1002','Leandro Martins Maria', 'Joaquim Dantes');

INSERT INTO phone_numbers (phone_number, registration) VALUES
('88973528860', '100000'),
('88973528861', '100001'),
('88973528865', '100002');

INSERT INTO phone_numbers (phone_number, registration) VALUES
('88973529860', '1000'),
('88973529861', '1001'),
('88973529865', '1002');
    
INSERT INTO categories (category, category_desc) VALUES
('Scientific articles', 'Material aimed at the composition and elaboration of academic documents.'),
('Applied mathematics', 'Books devoted to the study of fields of mathematics applied to real-life concepts.'),
('Pure mathematics', 'Books devoted to the study of mathematics used in higher education.');

INSERT INTO books (isbn_code, title, release_year, publisher, category_code, copies_available) VALUES
('8522112584', 'Calculus - Volume 1', '2013', 'Cengage', '3', '20'),
('8521630352', 'Fundamentals of Physics - Volume 1 - Mechanics', '2016', 'LTC', '2', '13'),
('8521630360', 'Fundamentals of Physics - Gravitation, Waves and Thermodynamics - Volume 2', '2016', 'LTC', '2', '15'),
('8521630379', 'Fundamentals of Physics - Electromagnetism - Volume 3', '2016', 'LTC', '2', '20'),
('8522125848', 'Calculus - vol. II: Volume 2', '2017', 'Cengage', '3', '12'),
('8540701693', 'Linear Algebra with Applications', '2012', 'Bookman', '3', '12'),
('8582602251', 'Calculus: Volume I', '2014', 'Bookman', '3', '6');

INSERT INTO authors (author_email, name, nationality) VALUES
('jamesStewart@edu.com', 'James Stewart', 'Canadian'),
('david_halliday@edu.com', 'David Halliday', 'American'),
('robert_resnick@edu.com', 'Robert Resnick', 'American'),
('jearl_walker310@edu.com', 'Jearl Walker', 'American'),
('sleon@edu.com', 'Steven J. Leon', 'American'),
('howard_anton@edu.com', 'Howard Anton', 'American');
    
INSERT INTO authors_write_books (isbn_code, author_email) VALUES
('8522112584', 'jamesStewart@edu.com'),
('8521630352', 'david_halliday@edu.com'),
('8521630352', 'robert_resnick@edu.com'),
('8521630352', 'jearl_walker310@edu.com'),
('8521630360', 'david_halliday@edu.com'),
('8521630360', 'robert_resnick@edu.com'),
('8521630360', 'jearl_walker310@edu.com'),
('8521630379', 'david_halliday@edu.com'),
('8521630379', 'robert_resnick@edu.com'),
('8521630379', 'jearl_walker310@edu.com'),
('8521630379', 'david_halliday@edu.com'),
('8521630379', 'robert_resnick@edu.com'),
('8521630379', 'jearl_walker310@edu.com'),
('8522125848', 'jamesStewart@edu.com'),
('8582602251', 'howard_anton@edu.com');

-- Users
DROP USER IF EXISTS 'admin'@'%';
CREATE USER 'admin'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON `college_library_db`.* TO 'admin'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'librarian'@'%';
CREATE USER 'librarian'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`books` TO 'librarian'@'%';
GRANT SELECT ON `college_library_db`.`users` TO 'librarian'@'%';
GRANT SELECT ON `college_library_db`.`students` TO 'librarian'@'%';
GRANT SELECT ON `college_library_db`.`employees` TO 'librarian'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'librarian'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'librarian'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'librarian'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'librarian'@'%';
GRANT SELECT, INSERT, DELETE, UPDATE ON `college_library_db`.`book_reservations` TO 'librarian'@'%';
GRANT SELECT, INSERT, DELETE, UPDATE ON `college_library_db`.`book_borrowings` TO 'librarian'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'lenoar_vieira'@'%';
CREATE USER 'lenoar_vieira'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'lenoar_vieira'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'lenoar_vieira'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'lenoar_vieira'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'lenoar_vieira'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'lenoar_vieira'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'lenoar_vieira'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'lenoar_vieira'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'lenoar_vieira'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'lenoar_vieira'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'alexandremmota'@'%';
CREATE USER 'alexandremmota'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'alexandremmota'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'alexandremmota'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'alexandremmota'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'alexandremmota'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'alexandremmota'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'alexandremmota'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'alexandremmota'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'alexandremmota'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'alexandremmota'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'adrianopaulo728'@'%';
CREATE USER 'adrianopaulo728'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'adrianopaulo728'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'adrianopaulo728'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'adrianopaulo728'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'adrianopaulo728'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'adrianopaulo728'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'adrianopaulo728'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'adrianopaulo728'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'adrianopaulo728'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'kevin_ferreira120'@'%';
CREATE USER 'kevin_ferreira120'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'kevin_ferreira120'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'kevin_ferreira120'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'kevin_ferreira120'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'kevin_ferreira120'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'kevin_ferreira120'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'kevin_ferreira120'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'kevin_ferreira120'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'kevin_ferreira120'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'kevin_ferreira120'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'leandro_paulla'@'%';
CREATE USER 'leandro_paulla'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'leandro_paulla'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'leandro_paulla'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'leandro_paulla'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'leandro_paulla'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'leandro_paulla'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'leandro_paulla'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'leandro_paulla'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'leandro_paulla'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'leandro_paulla'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'wagnerlopes'@'%';
CREATE USER 'wagnerlopes'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'wagnerlopes'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'wagnerlopes'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'wagnerlopes'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'wagnerlopes'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'wagnerlopes'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'wagnerlopes'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'wagnerlopes'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'wagnerlopes'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'wagnerlopes'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'rodriguesbastiao'@'%';
CREATE USER 'rodriguesbastiao'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'rodriguesbastiao'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'rodriguesbastiao'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'rodriguesbastiao'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'rodriguesbastiao'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'rodriguesbastiao'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'rodriguesbastiao'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'rodriguesbastiao'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'rodriguesbastiao'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'rodriguesbastiao'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'leia_albuquerque4829'@'%';
CREATE USER 'leia_albuquerque4829'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'leia_albuquerque4829'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'leia_albuquerque4829'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'leia_albuquerque4829'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'leia_albuquerque4829'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'leia_albuquerque4829'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'leia_albuquerque4829'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'leia_albuquerque4829'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'leia_albuquerque4829'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'leia_albuquerque4829'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'lucas_limamatos223'@'%';
CREATE USER 'lucas_limamatos223'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'lucas_limamatos223'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'lucas_limamatos223'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'lucas_limamatos223'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'lucas_limamatos223'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'lucas_limamatos223'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'lucas_limamatos223'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'lucas_limamatos223'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'lucas_limamatos223'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'lucas_limamatos223'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'joaquim_domingos'@'%';
CREATE USER 'joaquim_domingos'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'joaquim_domingos'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'joaquim_domingos'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'joaquim_domingos'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'joaquim_domingos'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'joaquim_domingos'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'joaquim_domingos'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'joaquim_domingos'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'joaquim_domingos'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'joaquim_domingos'@'%';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'leandro_martins'@'%';
CREATE USER 'leandro_martins'@'%' IDENTIFIED BY '1234';
GRANT SELECT ON `college_library_db`.`users` TO 'leandro_martins'@'%';
GRANT SELECT ON `college_library_db`.`books` TO 'leandro_martins'@'%';
GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO 'leandro_martins'@'%';
GRANT SELECT ON `college_library_db`.`book_borrowings` TO 'leandro_paulla'@'%';
GRANT SELECT ON `college_library_db`.`books_by_category` TO 'leandro_martins'@'%';
GRANT SELECT ON `college_library_db`.`books_by_publisher` TO 'leandro_martins'@'%';
GRANT SELECT ON `college_library_db`.`books_by_release` TO 'leandro_martins'@'%';
GRANT SELECT ON `college_library_db`.`books_by_author` TO 'leandro_martins'@'%';
GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO 'leandro_martins'@'%';
FLUSH PRIVILEGES;