-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 18-09-2025 a las 23:02:35
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

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `table`
--
ALTER TABLE `table`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `qr_code` (`qr_code`),
  ADD KEY `zone_id` (`zone_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `table`
--
ALTER TABLE `table`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=131;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `table`
--
ALTER TABLE `table`
  ADD CONSTRAINT `table_ibfk_1` FOREIGN KEY (`zone_id`) REFERENCES `zone` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
