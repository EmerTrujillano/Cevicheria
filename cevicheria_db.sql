-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 18-09-2025 a las 23:43:21
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `cevicheria_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `category`
--

CREATE TABLE `category` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `estacion` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `category`
--

INSERT INTO `category` (`id`, `name`, `description`, `estacion`, `created_at`) VALUES
(13, 'fríos', 'Deliciosos platos fríos de la casa', NULL, '2025-09-18 18:00:59'),
(14, 'calientes', 'Deliciosos platos calientes de la casa', NULL, '2025-09-18 18:00:59'),
(15, 'frituras', 'Deliciosos platos frituras de la casa', NULL, '2025-09-18 18:00:59'),
(16, 'bebidas', 'Deliciosos platos bebidas de la casa', NULL, '2025-09-18 18:00:59'),
(17, 'postres', 'Deliciosos platos postres de la casa', NULL, '2025-09-18 18:00:59'),
(18, 'acompañamientos', 'Deliciosos platos acompañamientos de la casa', NULL, '2025-09-18 18:00:59');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `floor`
--

CREATE TABLE `floor` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `floor`
--

INSERT INTO `floor` (`id`, `name`, `description`, `created_at`) VALUES
(1, 'Piso Principal', 'Piso principal del restaurante', '2025-09-18 16:34:42'),
(3, 'Segundo Piso', 'Segundo nivel del restaurante con vista panorámica', '2025-09-18 18:28:59');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `order`
--

CREATE TABLE `order` (
  `id` int(11) NOT NULL,
  `order_number` varchar(20) NOT NULL,
  `table_id` int(11) DEFAULT NULL,
  `waiter_id` int(11) NOT NULL,
  `customer_name` varchar(100) DEFAULT NULL,
  `order_type` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `special_instructions` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `served_at` datetime DEFAULT NULL,
  `paid_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `order`
--

INSERT INTO `order` (`id`, `order_number`, `table_id`, `waiter_id`, `customer_name`, `order_type`, `status`, `total_amount`, `special_instructions`, `created_at`, `served_at`, `paid_at`) VALUES
(1, 'COM-12668', 66, 2, NULL, 'dine_in', 'ready', 87.00, NULL, '2025-09-18 20:56:52', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `order_item`
--

CREATE TABLE `order_item` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `special_instructions` text DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `station_type` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `ready_at` datetime DEFAULT NULL,
  `served_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `order_item`
--

INSERT INTO `order_item` (`id`, `order_id`, `product_id`, `quantity`, `unit_price`, `total_price`, `special_instructions`, `status`, `station_type`, `created_at`, `started_at`, `ready_at`, `served_at`) VALUES
(1, 1, 65, 1, 37.00, 37.00, '[cocina1]', 'pending', NULL, '2025-09-18 20:56:52', NULL, NULL, NULL),
(2, 1, 59, 1, 25.00, 25.00, '[cocina1] sin picante', 'pending', NULL, '2025-09-18 20:56:52', NULL, NULL, NULL),
(3, 1, 59, 1, 25.00, 25.00, '[cocina1] sin cebolla, sin picante, con mucha leche de tigre, poco camote', 'pending', NULL, '2025-09-18 20:56:52', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `payment`
--

CREATE TABLE `payment` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `cashier_id` int(11) NOT NULL,
  `transaction_id` varchar(100) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `product`
--

CREATE TABLE `product` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock` int(11) DEFAULT NULL,
  `category_id` int(11) NOT NULL,
  `brand` varchar(50) DEFAULT NULL,
  `sku` varchar(20) DEFAULT NULL,
  `unit` varchar(20) DEFAULT NULL,
  `ingredients` text DEFAULT NULL,
  `tags` varchar(200) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `image_gallery` text DEFAULT NULL,
  `is_available` tinyint(1) DEFAULT NULL,
  `station_type` varchar(20) DEFAULT NULL,
  `preparation_time` int(11) DEFAULT NULL,
  `spice_level` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `product`
--

INSERT INTO `product` (`id`, `name`, `description`, `price`, `stock`, `category_id`, `brand`, `sku`, `unit`, `ingredients`, `tags`, `image_url`, `image_gallery`, `is_available`, `station_type`, `preparation_time`, `spice_level`, `created_at`, `last_updated`) VALUES
(59, 'Ceviche clásico', 'Delicioso ceviche clásico preparado con ingredientes frescos', 25.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(60, 'Ceviche mixto', 'Delicioso ceviche mixto preparado con ingredientes frescos', 27.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(61, 'Ceviche nikkei', 'Delicioso ceviche nikkei preparado con ingredientes frescos', 29.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(62, 'Tiradito al ají amarillo', 'Delicioso tiradito al ají amarillo preparado con ingredientes frescos', 31.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(63, 'Tiradito tres ajíes', 'Delicioso tiradito tres ajíes preparado con ingredientes frescos', 33.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(64, 'Leche de tigre', 'Delicioso leche de tigre preparado con ingredientes frescos', 35.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(65, 'Choritos a la chalaca', 'Delicioso choritos a la chalaca preparado con ingredientes frescos', 37.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(66, 'Causa limeña (pollo / pulpo / cangrejo)', 'Delicioso causa limeña (pollo / pulpo / cangrejo) preparado con ingredientes frescos', 39.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(67, 'Piqueo marino (frío)', 'Delicioso piqueo marino (frío) preparado con ingredientes frescos', 41.00, 0, 13, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(68, 'Arroz con mariscos', 'Delicioso arroz con mariscos preparado con ingredientes frescos', 30.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(69, 'Chaufa de mariscos', 'Delicioso chaufa de mariscos preparado con ingredientes frescos', 32.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(70, 'Tacu tacu con mariscos', 'Delicioso tacu tacu con mariscos preparado con ingredientes frescos', 34.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(71, 'Sudado de pescado', 'Delicioso sudado de pescado preparado con ingredientes frescos', 36.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(72, 'Parihuela', 'Delicioso parihuela preparado con ingredientes frescos', 38.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(73, 'Pescado a lo macho', 'Delicioso pescado a lo macho preparado con ingredientes frescos', 40.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(74, 'Ají de gallina', 'Delicioso ají de gallina preparado con ingredientes frescos', 42.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(75, 'Piqueo marino (caliente)', 'Delicioso piqueo marino (caliente) preparado con ingredientes frescos', 44.00, 0, 14, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(76, 'Jalea mixta', 'Delicioso jalea mixta preparado con ingredientes frescos', 28.00, 0, 15, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(77, 'Chicharrón de calamar', 'Delicioso chicharrón de calamar preparado con ingredientes frescos', 30.00, 0, 15, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(78, 'Pulpo a la parrilla', 'Delicioso pulpo a la parrilla preparado con ingredientes frescos', 32.00, 0, 15, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(79, 'Lomo saltado', 'Delicioso lomo saltado preparado con ingredientes frescos', 34.00, 0, 15, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(80, 'Chicha morada', 'Delicioso chicha morada preparado con ingredientes frescos', 8.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(81, 'Chicha de jora', 'Delicioso chicha de jora preparado con ingredientes frescos', 10.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(82, 'Inca Kola', 'Delicioso inca kola preparado con ingredientes frescos', 12.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(83, 'Jugo de maracuyá', 'Delicioso jugo de maracuyá preparado con ingredientes frescos', 14.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(84, 'Limonada', 'Delicioso limonada preparado con ingredientes frescos', 16.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(85, 'Agua sin/con gas', 'Delicioso agua sin/con gas preparado con ingredientes frescos', 18.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(86, 'Pisco Sour', 'Delicioso pisco sour preparado con ingredientes frescos', 21.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(87, 'Chilcano (clásico, maracuyá, jengibre)', 'Delicioso chilcano (clásico, maracuyá, jengibre) preparado con ingredientes frescos', 22.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(88, 'Sangría', 'Delicioso sangría preparado con ingredientes frescos', 23.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(89, 'Cerveza (Pilsen, Cusqueña, artesanal)', 'Delicioso cerveza (pilsen, cusqueña, artesanal) preparado con ingredientes frescos', 12.00, 0, 16, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(90, 'Suspiro limeño', 'Delicioso suspiro limeño preparado con ingredientes frescos', 12.00, 0, 17, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(91, 'Mazamorra morada', 'Delicioso mazamorra morada preparado con ingredientes frescos', 14.00, 0, 17, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(92, 'Arroz con leche', 'Delicioso arroz con leche preparado con ingredientes frescos', 16.00, 0, 17, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(93, 'Tres leches', 'Delicioso tres leches preparado con ingredientes frescos', 18.00, 0, 17, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(94, 'Helado de maracuyá o chirimoya', 'Delicioso helado de maracuyá o chirimoya preparado con ingredientes frescos', 20.00, 0, 17, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(95, 'Camote glaseado', 'Delicioso camote glaseado preparado con ingredientes frescos', 10.00, 0, 18, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(96, 'Choclo con queso', 'Delicioso choclo con queso preparado con ingredientes frescos', 12.00, 0, 18, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(97, 'Papa o yuca frita', 'Delicioso papa o yuca frita preparado con ingredientes frescos', 14.00, 0, 18, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(98, 'Ensalada criolla', 'Delicioso ensalada criolla preparado con ingredientes frescos', 16.00, 0, 18, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59'),
(99, 'Pan al ajo', 'Delicioso pan al ajo preparado con ingredientes frescos', 18.00, 0, 18, NULL, NULL, NULL, 'Ingredientes frescos de primera calidad', NULL, NULL, NULL, 1, 'hot', 15, 'mild', '2025-09-18 18:00:59', '2025-09-18 18:00:59');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `review`
--

CREATE TABLE `review` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `customer_name` varchar(100) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `is_approved` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `approved_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `survey`
--

CREATE TABLE `survey` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `table`
--

CREATE TABLE `table` (
  `id` int(11) NOT NULL,
  `number` varchar(10) NOT NULL,
  `capacity` int(11) NOT NULL,
  `zone_id` int(11) NOT NULL,
  `status` varchar(20) NOT NULL,
  `qr_code` varchar(255) DEFAULT NULL,
  `qr_scanned_at` datetime DEFAULT NULL,
  `qr_expires_at` datetime DEFAULT NULL,
  `qr_session_id` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `table`
--

INSERT INTO `table` (`id`, `number`, `capacity`, `zone_id`, `status`, `qr_code`, `qr_scanned_at`, `qr_expires_at`, `qr_session_id`, `created_at`) VALUES
(66, '1', 4, 11, 'ocupada', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(67, '2', 4, 11, 'ocupada', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(68, '3', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(69, '4', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(70, '5', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(71, '6', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(72, '7', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(73, '8', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(74, '9', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(75, '10', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(76, '11', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(77, '12', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(78, '13', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(79, '14', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(80, '15', 4, 11, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(81, 'B1', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(82, 'B2', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(83, 'B3', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(84, 'B4', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(85, 'B5', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(86, 'B6', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(87, 'B7', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(88, 'B8', 2, 12, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(89, 'F1', 6, 13, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(90, 'F2', 6, 13, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(91, 'F3', 6, 13, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(92, 'F4', 6, 13, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(93, 'F5', 6, 13, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(94, 'F6', 6, 13, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(95, 'V1', 4, 14, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(96, 'V2', 4, 14, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(97, 'V3', 4, 14, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(98, 'V4', 4, 14, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(99, 'V5', 4, 14, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(100, 'V6', 4, 14, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(101, 'S1', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(102, 'S2', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(103, 'S3', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(104, 'S4', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(105, 'S5', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(106, 'S6', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(107, 'S7', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(108, 'S8', 4, 15, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(109, 'T1', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(110, 'T2', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(111, 'T3', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(112, 'T4', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(113, 'T5', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(114, 'T6', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(115, 'T7', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(116, 'T8', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(117, 'T9', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(118, 'T10', 4, 16, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(119, 'P1', 8, 17, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(120, 'P2', 8, 17, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(121, 'P3', 8, 17, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(122, 'P4', 8, 17, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(123, 'L1', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(124, 'L2', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(125, 'L3', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(126, 'L4', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(127, 'L5', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(128, 'L6', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(129, 'L7', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42'),
(130, 'L8', 4, 18, 'libre', NULL, NULL, NULL, NULL, '2025-09-18 19:04:42');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `temporary_permission`
--

CREATE TABLE `temporary_permission` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `granted_by` int(11) NOT NULL,
  `area` varchar(50) NOT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `reason` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(80) NOT NULL,
  `password` varchar(120) NOT NULL,
  `role` varchar(20) NOT NULL,
  `estacion` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `current_session_token` varchar(255) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `last_activity` datetime DEFAULT NULL,
  `session_expires_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `user`
--

INSERT INTO `user` (`id`, `username`, `password`, `role`, `estacion`, `created_at`, `current_session_token`, `last_login`, `last_activity`, `session_expires_at`) VALUES
(1, 'admin', '$2b$12$DiII8Yxid0/Avl1a0ysFoOswJ49a.aRVGVBP/VOOqd6VklC.3DULG', 'admin', NULL, '2025-09-18 11:34:42', 'sess_SdYef6z6gRxWb_I56IVvTX7FBJ8qu5ETQhogHuPxnjg', '2025-09-18 15:18:53', '2025-09-18 15:18:53', '2025-09-19 15:18:53'),
(2, 'mozo1', '$2b$12$dKL1eUD1Q1K33CVIdwJ29.cN6t7wsZ/yx/QxXsGUBiFqBRTpSUy.G', 'mozo', NULL, '2025-09-18 11:34:42', 'sess_lpEg0l9RdlhXQtMDeytuDlY8foDW-yD4dFlMc8UmMK8', '2025-09-18 16:21:59', '2025-09-18 16:21:59', '2025-09-19 16:21:59'),
(3, 'mozo2', '$2b$12$GCgjOT2TFieVgijCSoXYUuBQrpLy.58fXRagIlw0NP7aM7kvNKROy', 'mozo', NULL, '2025-09-18 11:34:42', 'sess_2lodqIhNtS9IXZZ-5WE33m62UFm1aalr9ft1bdMu28M', '2025-09-18 15:00:49', '2025-09-18 15:00:49', '2025-09-19 15:00:49'),
(4, 'cocina1', '$2b$12$KlfZvagdNpMTh1wiippPAOO4pjN6oZojSWQDf0j83S7JDs4zGcfTy', 'cocina', 'frios', '2025-09-18 11:34:42', 'sess_8nN4EBqyQvJcIrnQSp2tBfCaLM3aA2GrpWRz3YXnbqg', '2025-09-18 15:55:09', '2025-09-18 15:55:09', '2025-09-19 15:55:09'),
(5, 'cocina2', '$2b$12$0k3ueYCtozkDzKT/cMcqL.V4olR1OjDxsoI/168xMCA.TQp.ObB3e', 'cocina', 'calientes', '2025-09-18 11:34:42', NULL, NULL, NULL, NULL),
(6, 'cocina3', '$2b$12$.rNfbyxpjWMIE.7PNnEkDeYnfptDin7X6zcFjMVjtrvkbHiYVMtni', 'cocina', 'frituras', '2025-09-18 11:34:42', NULL, NULL, NULL, NULL),
(7, 'cocina4', '$2b$12$vkVy0wTyO3wuCTpTzbOoCOMTHEBgXKujqBIea7l6NZmxx3L9Q1yfW', 'cocina', 'bebidas', '2025-09-18 11:34:42', NULL, NULL, NULL, NULL),
(8, 'cocina5', '$2b$12$cz1yQnGbt5ASJ9Kb1cei0utKVkSr2x1zY3KCPvAYaIAgZH1xKsCoy', 'cocina', 'postres', '2025-09-18 11:34:42', NULL, NULL, NULL, NULL),
(9, 'cocina6', '$2b$12$NkzDXBZnKGSQ6dLt4Ufn7.6.TwULNoc1ioYtG3k8Z53BrMB15Prfy', 'cocina', 'acomp', '2025-09-18 11:34:42', NULL, NULL, NULL, NULL),
(10, 'cajero1', '$2b$12$JXnZJDPVNKvXZNcy2RWfu.6GYCpMdQ/rja2SR7.Gq1kNwMRZIfCUG', 'cajero', NULL, '2025-09-18 11:34:42', 'sess_LPuMUCewkRWA6feVy36t7IM7SDqOwxSDMXE3peLaNnk', '2025-09-18 11:58:59', '2025-09-18 11:58:59', '2025-09-19 11:58:59');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_sessions`
--

CREATE TABLE `user_sessions` (
  `id` int(11) NOT NULL,
  `session_id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `device_info` varchar(500) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `last_activity` datetime NOT NULL,
  `expires_at` datetime NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `logout_reason` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `user_sessions`
--

INSERT INTO `user_sessions` (`id`, `session_id`, `user_id`, `device_info`, `ip_address`, `created_at`, `last_activity`, `expires_at`, `is_active`, `logout_reason`) VALUES
(1, 'sess_61M3UxsXgdLsmjutsiiPHXXfNoaTmaZaKLMt9KkIqrk', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:46:47', '2025-09-18 11:46:47', '2025-09-19 11:46:47', 0, 'admin_closed'),
(2, 'sess_hDUIq6aaqP71LvtqHVIBLWmCljFfPx-0M5vdreXM6Hg', 1, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:47:49', '2025-09-18 11:47:49', '2025-09-19 11:47:49', 0, 'manual_logout'),
(3, 'sess_y-oaNjSBZlLjsIqPPKYSFw-6RRc04x3-OefgCqe3cUE', 3, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:48:20', '2025-09-18 11:48:20', '2025-09-19 11:48:20', 0, 'cleanup_manual'),
(4, 'sess_QVRiy2q4vtlnAj-kmQDyRarcPfAFqCpNKftHo9kQ_Ug', 1, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:48:33', '2025-09-18 11:48:33', '2025-09-19 11:48:33', 0, 'manual_logout'),
(5, 'sess_82zGdSrrhi-J9QfF6WH_-Jnio9Q6j6cUVS-DrZCWy1c', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:49:14', '2025-09-18 11:49:14', '2025-09-19 11:49:14', 0, 'cleanup_manual'),
(6, 'sess_RiVgnlO4gD-HIedBOypvz_IN3hrw5LiSZLJmcqTKFU0', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:53:57', '2025-09-18 11:53:57', '2025-09-19 11:53:57', 0, 'manual_cleanup'),
(7, 'sess_zmOtUfgIGrz-N05fSuwVgjIe2zGt9-Jih3SvxGwbQRU', 1, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:54:25', '2025-09-18 11:54:25', '2025-09-19 11:54:25', 0, 'manual_logout'),
(8, 'sess_CPlHD18Q90LXNpQuwRbP7rtVJiDVtj7OoR0ZCiIkGck', 1, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:58:46', '2025-09-18 11:58:46', '2025-09-19 11:58:46', 0, 'manual_logout'),
(9, 'sess_LPuMUCewkRWA6feVy36t7IM7SDqOwxSDMXE3peLaNnk', 10, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:58:59', '2025-09-18 11:58:59', '2025-09-19 11:58:59', 0, NULL),
(10, 'sess_AN3Ss1SwM5HJtooeAz9Z3UZjkqMWs4Z2__eoDY3mecc', 4, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:59:09', '2025-09-18 11:59:09', '2025-09-19 11:59:09', 0, NULL),
(11, 'sess_PaOf4lelyfhtemxjqeKWm-2tr7FfOiulv-sfcomaw0s', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 11:59:17', '2025-09-18 11:59:17', '2025-09-19 11:59:17', 0, NULL),
(12, 'sess_69MxkJ8VObbkS8qDL2FvXuB0PyAjDBxbtBZHMOLfgcQ', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:07:52', '2025-09-18 12:07:52', '2025-09-19 12:07:52', 0, 'new_login_replacement'),
(13, 'sess_l2J4CrmbXNUGFmuX2vtqEO35y7ROausXvMpnHY7nLFQ', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:09:59', '2025-09-18 12:09:59', '2025-09-19 12:09:59', 0, 'new_login_replacement'),
(14, 'sess_T3W2TvHWvgakdvW97i7DA3P31M7FrL1CF6dPuihby2E', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:12:23', '2025-09-18 12:12:23', '2025-09-19 12:12:23', 0, 'new_login_replacement'),
(15, 'sess_O3z3PHD2PykOlt2Pg8AHd0FjyLk59ajZ67mbHsgbuzI', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:17:06', '2025-09-18 12:17:06', '2025-09-19 12:17:06', 0, 'admin_closed'),
(16, 'sess_vP1HS3B2A-zH1xCoEYN1a8fcRe1vfVom_qklKym465Q', 1, 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36', '192.168.0.4', '2025-09-18 12:20:15', '2025-09-18 12:20:15', '2025-09-19 12:20:15', 0, 'manual_logout'),
(17, 'sess_y548BjHRoTrNLXv-QI98KCCxtVYnk933paDUPtxoZTI', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:32:16', '2025-09-18 12:32:16', '2025-09-19 12:32:16', 0, 'new_login_replacement'),
(18, 'sess_aDg4Pkeg2yzqAyyudgpg0-VDIUek5ggPgZii2uY2UbY', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:32:36', '2025-09-18 12:32:36', '2025-09-19 12:32:36', 0, 'new_login_replacement'),
(19, 'sess_Ua8pWkUcMlpuOLfFlE7WP-w_Pf3TIlJSQ20Kibp8ZGY', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:32:45', '2025-09-18 12:32:45', '2025-09-19 12:32:45', 0, 'new_login_replacement'),
(20, 'sess_x_BuI8p9nxZb0LbyqtdEw80hfRVOHRs_JVHNcDrTG5U', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:36:11', '2025-09-18 12:36:11', '2025-09-19 12:36:11', 0, 'new_login_replacement'),
(21, 'sess_2rDqzirigrophGhreeEma3juIq3J4lUHXu08hB92JgA', 3, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:39:08', '2025-09-18 12:39:08', '2025-09-19 12:39:08', 0, 'new_login_replacement'),
(22, 'sess_vDcQ2UCrqZbsWvkvtSlLkw1wGTLLGId-OjFevAFw7Uk', 3, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:39:46', '2025-09-18 12:39:46', '2025-09-19 12:39:46', 0, 'new_login_replacement'),
(23, 'sess_TwyOkRQi7r6Pp3cCxmOPwS-NmFExzLIAPZ1jTIdYb-8', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:40:40', '2025-09-18 12:40:40', '2025-09-19 12:40:40', 0, 'new_login_replacement'),
(24, 'sess_QMppkyp_ShPCH9HQo_weda3JG5zS-lALTlZpEY5EnWw', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:42:32', '2025-09-18 12:42:32', '2025-09-19 12:42:32', 0, 'new_login_replacement'),
(25, 'sess_9xinJ8QuPp4wVhlbASwejMPKtndqu7b8TTPhrjJG96E', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:49:13', '2025-09-18 12:49:13', '2025-09-19 12:49:13', 0, 'manual_logout'),
(26, 'sess_z9jQ0cA44-g5Q-shTWZovfjkuPHlY3MHtubcD4-oP7c', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 12:55:26', '2025-09-18 12:55:26', '2025-09-19 12:55:26', 0, 'new_login_replacement'),
(27, 'sess_YL7CgdRUrqk2AWWqV4_Bz8wXqM0qSYLzC3Ll3t3vS0M', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 13:04:47', '2025-09-18 13:04:47', '2025-09-19 13:04:47', 0, 'new_login_replacement'),
(28, 'sess_H8UYKt8N5w4fmxFGxDnGu72CtX6hEMVg2-U9AAqg64E', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 13:14:51', '2025-09-18 13:14:51', '2025-09-19 13:14:51', 0, 'new_login_replacement'),
(29, 'sess_oM5W6Rh5OJJWEaC30DWDej8cgpjtbLNjWUmQ56otv6Q', 1, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 13:17:14', '2025-09-18 13:17:14', '2025-09-19 13:17:14', 0, 'new_login_replacement'),
(30, 'sess_s1a0hCsu1c17VBs0ExVaMViUthiMPJ0L8xzFZyjRl0E', 1, 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36', '192.168.0.7', '2025-09-18 13:18:34', '2025-09-18 13:18:34', '2025-09-19 13:18:34', 0, 'new_login_replacement'),
(31, 'sess_0zrc-J_1hLhbUA1HZ3jKUCuBJLaJkEj2rbgbzHs1cmc', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 13:30:23', '2025-09-18 13:30:23', '2025-09-19 13:30:23', 0, 'new_login_replacement'),
(32, 'sess_VdHoGku2UnRbN0bfaOpe3kV-LX-v-q-D_Ky44KgJwtU', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 13:37:31', '2025-09-18 13:37:31', '2025-09-19 13:37:31', 0, 'new_login_replacement'),
(33, 'sess_t5_JDeOw1lPAunoFTWXa48mK8TOvImgrfTw9rmZwrY8', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 13:55:30', '2025-09-18 13:55:30', '2025-09-19 13:55:30', 0, 'new_login_replacement'),
(34, 'sess_NJBl0tDMPoRmsrOgiPpwIOZpVtxYr8MA9gdROTiPppw', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 13:55:30', '2025-09-18 13:55:30', '2025-09-19 13:55:30', 0, 'new_login_replacement'),
(35, 'sess_cUISqpk47XEPB_XIq56tn7CeTLqgPThBTwucLDX3inQ', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 14:11:15', '2025-09-18 14:11:15', '2025-09-19 14:11:15', 0, 'new_login_replacement'),
(36, 'sess_ol-DAT3YkjDwCQ6W3m1zi1LT5QI6d37uZDDpmYolSYw', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '192.168.0.5', '2025-09-18 14:11:16', '2025-09-18 14:11:16', '2025-09-19 14:11:16', 0, 'new_login_replacement'),
(37, 'sess_52IMbqJaZvHmjr-T9oBpooNEMrrLfsDA9tUIAdBaGYI', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 14:19:14', '2025-09-18 14:19:14', '2025-09-19 14:19:14', 0, 'manual_logout'),
(38, 'sess_v_UW0rdtrIyqhT1NWIfXRXyNbSFLjZXcrwijeDh5RnQ', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 14:24:43', '2025-09-18 14:24:43', '2025-09-19 14:24:43', 0, 'new_login_replacement'),
(39, 'sess_3FCf6JQLJglM1z4c7765-qavTWkoLccWXOL_q_CjJ2Q', 2, 'python-requests/2.32.5', '127.0.0.1', '2025-09-18 14:47:50', '2025-09-18 14:47:50', '2025-09-19 14:47:50', 0, 'new_login_replacement'),
(40, 'sess_2lodqIhNtS9IXZZ-5WE33m62UFm1aalr9ft1bdMu28M', 3, 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36', '10.37.137.233', '2025-09-18 15:00:49', '2025-09-18 15:00:49', '2025-09-19 15:00:49', 0, 'admin_closed'),
(41, 'sess_TFFUWwDOwJ4FHgMCyW8x2wY0LzOSbIRiMDPANJcWIzA', 2, 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36', '10.37.137.233', '2025-09-18 15:09:01', '2025-09-18 15:09:01', '2025-09-19 15:09:01', 0, 'new_login_replacement'),
(42, 'sess_iWrdkrlHhWX6PO5Wl5hezbj4bvb4PkscKKBZifTaruo', 2, 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36', '10.37.137.233', '2025-09-18 15:09:04', '2025-09-18 15:09:04', '2025-09-19 15:09:04', 0, 'admin_closed'),
(43, 'sess_SdYef6z6gRxWb_I56IVvTX7FBJ8qu5ETQhogHuPxnjg', 1, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '10.37.137.170', '2025-09-18 15:18:53', '2025-09-18 15:18:53', '2025-09-19 15:18:53', 1, NULL),
(44, 'sess_RrKeU1SJ41TFiOBZtot14Q1jTK-2J3apYfD16kSE-_0', 4, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 15:25:22', '2025-09-18 15:25:22', '2025-09-19 15:25:22', 0, 'new_login_replacement'),
(45, 'sess_od1hTOsFJzikCsZcqU0IQZ5dP3BBPCMVFfCZSTKe7EE', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 15:27:53', '2025-09-18 15:27:53', '2025-09-19 15:27:53', 0, 'new_login_replacement'),
(46, 'sess_BmNaKC9ulOPLR5a2fnzps4zloWrLfKJuRL8J_idMMH0', 4, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 15:39:34', '2025-09-18 15:39:34', '2025-09-19 15:39:34', 0, 'new_login_replacement'),
(47, 'sess_cBmAlVnniwdYNn_B_GY1eR1jiOxLqOW5Wb3fqSnmb_k', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 15:39:53', '2025-09-18 15:39:53', '2025-09-19 15:39:53', 0, 'manual_logout'),
(48, 'sess_w29OQhHm16bpmS-vMvmtq6qZrTx7S7kRB0RLpO5mIRY', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 15:41:12', '2025-09-18 15:41:12', '2025-09-19 15:41:12', 0, 'new_login_replacement'),
(49, 'sess_DUUYxEgFahmcxtWZPXK_1-un6GbLxT7MXMPD1USopK0', 4, 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36', '10.37.137.233', '2025-09-18 15:41:37', '2025-09-18 15:41:37', '2025-09-19 15:41:37', 0, 'new_login_replacement'),
(50, 'sess_IefdRfuPtBT35EYmjaQSOfVuipwUWCMYIKjeCEzhoDs', 4, 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36', '10.37.137.233', '2025-09-18 15:54:54', '2025-09-18 15:54:54', '2025-09-19 15:54:54', 0, 'new_login_replacement'),
(51, 'sess_8nN4EBqyQvJcIrnQSp2tBfCaLM3aA2GrpWRz3YXnbqg', 4, 'Mozilla/5.0 (Windows NT; Windows NT 10.0; es-PE) WindowsPowerShell/5.1.19041.6328', '127.0.0.1', '2025-09-18 15:55:09', '2025-09-18 15:55:09', '2025-09-19 15:55:09', 1, NULL),
(52, 'sess_lpEg0l9RdlhXQtMDeytuDlY8foDW-yD4dFlMc8UmMK8', 2, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', '127.0.0.1', '2025-09-18 16:21:59', '2025-09-18 16:21:59', '2025-09-19 16:21:59', 1, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `zone`
--

CREATE TABLE `zone` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `floor_id` int(11) NOT NULL,
  `zone_type` varchar(30) NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `zone`
--

INSERT INTO `zone` (`id`, `name`, `description`, `floor_id`, `zone_type`, `created_at`) VALUES
(11, 'Zona Principal', 'Mesas principales del restaurante', 1, 'dining', '2025-09-18 19:04:42'),
(12, 'Zona Barra', 'Mesas tipo barra para grupos pequeños', 1, 'dining', '2025-09-18 19:04:42'),
(13, 'Zona Familiar', 'Mesas grandes para familias', 1, 'dining', '2025-09-18 19:04:42'),
(14, 'Zona Ventana', 'Mesas junto a las ventanas', 1, 'dining', '2025-09-18 19:04:42'),
(15, 'Sala VIP', 'Zona exclusiva del segundo piso', 3, 'dining', '2025-09-18 19:04:42'),
(16, 'Terraza', 'Mesas en la terraza', 3, 'dining', '2025-09-18 19:04:42'),
(17, 'Salón Privado', 'Salón para eventos privados', 3, 'dining', '2025-09-18 19:04:42'),
(18, 'Zona Balcón', 'Mesas con vista al exterior', 3, 'dining', '2025-09-18 19:04:42');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `category`
--
ALTER TABLE `category`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `floor`
--
ALTER TABLE `floor`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `order`
--
ALTER TABLE `order`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `table_id` (`table_id`),
  ADD KEY `waiter_id` (`waiter_id`);

--
-- Indices de la tabla `order_item`
--
ALTER TABLE `order_item`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indices de la tabla `payment`
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `cashier_id` (`cashier_id`);

--
-- Indices de la tabla `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `sku` (`sku`),
  ADD KEY `category_id` (`category_id`);

--
-- Indices de la tabla `review`
--
ALTER TABLE `review`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `approved_by` (`approved_by`);

--
-- Indices de la tabla `survey`
--
ALTER TABLE `survey`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indices de la tabla `table`
--
ALTER TABLE `table`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `qr_code` (`qr_code`),
  ADD KEY `zone_id` (`zone_id`);

--
-- Indices de la tabla `temporary_permission`
--
ALTER TABLE `temporary_permission`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `granted_by` (`granted_by`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_user_sessions_session_id` (`session_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indices de la tabla `zone`
--
ALTER TABLE `zone`
  ADD PRIMARY KEY (`id`),
  ADD KEY `floor_id` (`floor_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `category`
--
ALTER TABLE `category`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `floor`
--
ALTER TABLE `floor`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `order`
--
ALTER TABLE `order`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `order_item`
--
ALTER TABLE `order_item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `payment`
--
ALTER TABLE `payment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `product`
--
ALTER TABLE `product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=100;

--
-- AUTO_INCREMENT de la tabla `review`
--
ALTER TABLE `review`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `survey`
--
ALTER TABLE `survey`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `table`
--
ALTER TABLE `table`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=131;

--
-- AUTO_INCREMENT de la tabla `temporary_permission`
--
ALTER TABLE `temporary_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `user_sessions`
--
ALTER TABLE `user_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `zone`
--
ALTER TABLE `zone`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `order`
--
ALTER TABLE `order`
  ADD CONSTRAINT `order_ibfk_1` FOREIGN KEY (`table_id`) REFERENCES `table` (`id`),
  ADD CONSTRAINT `order_ibfk_2` FOREIGN KEY (`waiter_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `order_item`
--
ALTER TABLE `order_item`
  ADD CONSTRAINT `order_item_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`),
  ADD CONSTRAINT `order_item_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);

--
-- Filtros para la tabla `payment`
--
ALTER TABLE `payment`
  ADD CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`),
  ADD CONSTRAINT `payment_ibfk_2` FOREIGN KEY (`cashier_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`);

--
-- Filtros para la tabla `review`
--
ALTER TABLE `review`
  ADD CONSTRAINT `review_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`),
  ADD CONSTRAINT `review_ibfk_2` FOREIGN KEY (`approved_by`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `survey`
--
ALTER TABLE `survey`
  ADD CONSTRAINT `survey_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`),
  ADD CONSTRAINT `survey_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `table`
--
ALTER TABLE `table`
  ADD CONSTRAINT `table_ibfk_1` FOREIGN KEY (`zone_id`) REFERENCES `zone` (`id`);

--
-- Filtros para la tabla `temporary_permission`
--
ALTER TABLE `temporary_permission`
  ADD CONSTRAINT `temporary_permission_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `temporary_permission_ibfk_2` FOREIGN KEY (`granted_by`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `zone`
--
ALTER TABLE `zone`
  ADD CONSTRAINT `zone_ibfk_1` FOREIGN KEY (`floor_id`) REFERENCES `floor` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
