-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Generation Time: Jun 16, 2025 at 09:39 AM
-- Server version: 8.0.32
-- PHP Version: 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `headless_pm`
--

-- --------------------------------------------------------

--
-- Table structure for table `agent`
--

CREATE TABLE `agent` (
  `id` int NOT NULL,
  `agent_id` varchar(255) NOT NULL,
  `role` enum('FRONTEND_DEV','BACKEND_DEV','QA','ARCHITECT','PM') NOT NULL,
  `level` enum('JUNIOR','SENIOR','PRINCIPAL') NOT NULL,
  `last_seen` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `agent`
--

INSERT INTO `agent` (`id`, `agent_id`, `role`, `level`, `last_seen`) VALUES
(1, 'pm_principal_001', 'PM', 'PRINCIPAL', '2025-06-16 09:05:51');

-- --------------------------------------------------------

--
-- Table structure for table `changelog`
--

CREATE TABLE `changelog` (
  `id` int NOT NULL,
  `task_id` int NOT NULL,
  `old_status` enum('CREATED','EVALUATION','APPROVED','UNDER_WORK','DEV_DONE','QA_DONE','DOCUMENTATION_DONE','COMMITTED') NOT NULL,
  `new_status` enum('CREATED','EVALUATION','APPROVED','UNDER_WORK','DEV_DONE','QA_DONE','DOCUMENTATION_DONE','COMMITTED') NOT NULL,
  `changed_by` varchar(255) NOT NULL,
  `notes` text DEFAULT NULL,
  `changed_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `changelog`
--

INSERT INTO `changelog` (`id`, `task_id`, `old_status`, `new_status`, `changed_by`, `notes`, `changed_at`) VALUES
(1, 1, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:09:17'),
(2, 2, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:09:38'),
(3, 3, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:10:33'),
(4, 4, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:10:50'),
(5, 5, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:16:25'),
(6, 6, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:16:36'),
(7, 7, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:16:46'),
(8, 8, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:16:58'),
(9, 9, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:17:10'),
(10, 10, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:17:21'),
(11, 11, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:17:31'),
(12, 12, 'CREATED', 'CREATED', 'pm_principal_001', 'Task created', '2025-06-16 09:17:42');

-- --------------------------------------------------------

--
-- Table structure for table `document`
--

CREATE TABLE `document` (
  `id` int NOT NULL,
  `doc_type` enum('STANDUP','CRITICAL_ISSUE','SERVICE_STATUS','UPDATE') NOT NULL,
  `author_id` varchar(255) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` text NOT NULL,
  `meta_data` json DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `expires_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `document`
--

INSERT INTO `document` (`id`, `doc_type`, `author_id`, `title`, `content`, `meta_data`, `created_at`, `updated_at`, `expires_at`) VALUES
(1, 'UPDATE', 'pm_principal_001', 'Sprint Status - Week of 2025-06-16', 'Current sprint focus: Timeline Release v1.2 features including X-ray timeline UI, WebSocket integration, and email system. Backend APIs are ready. Frontend implementation in progress.', 'null', '2025-06-16 09:09:52', '2025-06-16 09:09:52', NULL),
(2, 'UPDATE', 'pm_principal_001', 'Agent Swarm Toolkit - Project Overview', 'LLM integration framework with 5 paradigms: Direct LLM, Agent System, Swarm System, Async Workflows, and Operator Dashboard. Current status: v1.1 Control Plane complete with 99.1% test coverage. Working on v1.2 Timeline Release.', 'null', '2025-06-16 09:11:16', '2025-06-16 09:11:16', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `epic`
--

CREATE TABLE `epic` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `epic`
--

INSERT INTO `epic` (`id`, `name`, `description`, `created_at`) VALUES
(1, 'Timeline Release v1.2', 'X-ray execution timeline, email integration, and performance improvements. Target: 2025-06-30', '2025-06-16 09:08:17'),
(2, 'Enterprise Release v2.0', 'Multi-tenancy support, advanced security features, and marketplace launch. Target: Q4 2024', '2025-06-16 09:08:26'),
(3, 'Technical Debt Reduction', 'Address architecture compatibility, testing improvements, and performance optimizations', '2025-06-16 09:08:34'),
(4, 'Frontend Excellence Initiative', 'Complete remaining placeholder pages, enhance real-time features, and polish user experience', '2025-06-16 09:15:43');

-- --------------------------------------------------------

--
-- Table structure for table `feature`
--

CREATE TABLE `feature` (
  `id` int NOT NULL,
  `epic_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `feature`
--

INSERT INTO `feature` (`id`, `epic_id`, `name`, `description`) VALUES
(1, 1, 'X-ray Timeline Frontend', 'Implement visual execution timeline in the frontend UI with real-time updates'),
(2, 1, 'WebSocket Integration', 'Real-time UI updates using ws://localhost:8000/api/v1/ws for live execution status'),
(3, 1, 'Email Integration', 'AWS SES integration for system emails and Gmail API for agent email capabilities'),
(4, 3, 'Test Suite Improvements', 'Fix test isolation issues and improve test coverage'),
(5, 4, 'Placeholder Page Completion', 'Complete implementation of 12 remaining placeholder pages with full functionality'),
(6, 4, 'Performance Optimization', 'Achieve sub-2s page loads, implement code splitting, and optimize bundle size');

-- --------------------------------------------------------

--
-- Table structure for table `mention`
--

CREATE TABLE `mention` (
  `id` int NOT NULL,
  `document_id` int DEFAULT NULL,
  `task_id` int DEFAULT NULL,
  `mentioned_agent_id` varchar(255) NOT NULL,
  `created_by` varchar(255) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `service`
--

CREATE TABLE `service` (
  `id` int NOT NULL,
  `service_name` varchar(100) NOT NULL,
  `owner_agent_id` varchar(255) NOT NULL,
  `port` int DEFAULT NULL,
  `status` enum('UP','DOWN','STARTING') NOT NULL,
  `last_heartbeat` datetime DEFAULT NULL,
  `meta_data` json DEFAULT NULL,
  `updated_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `task`
--

CREATE TABLE `task` (
  `id` int NOT NULL,
  `feature_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `created_by_id` int NOT NULL,
  `target_role` enum('FRONTEND_DEV','BACKEND_DEV','QA','ARCHITECT','PM') NOT NULL,
  `difficulty` enum('JUNIOR','SENIOR','PRINCIPAL') NOT NULL,
  `complexity` enum('MINOR','MAJOR') NOT NULL,
  `branch` varchar(255) NOT NULL,
  `status` enum('CREATED','EVALUATION','APPROVED','UNDER_WORK','DEV_DONE','QA_DONE','DOCUMENTATION_DONE','COMMITTED') NOT NULL,
  `locked_by_id` int DEFAULT NULL,
  `locked_at` datetime DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `task`
--

INSERT INTO `task` (`id`, `feature_id`, `title`, `description`, `created_by_id`, `target_role`, `difficulty`, `complexity`, `branch`, `status`, `locked_by_id`, `locked_at`, `notes`, `created_at`, `updated_at`) VALUES
(1, 1, 'Implement X-ray timeline component', 'Create React component for visual execution timeline with D3.js or similar library. Should show task dependencies, execution status, and timing information.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/xray-timeline', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:09:17', '2025-06-16 09:09:17'),
(2, 2, 'Setup WebSocket connection handler', 'Implement WebSocket client in React app to connect to ws://localhost:8000/api/v1/ws. Handle connection, reconnection, and message routing.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/websocket-integration', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:09:38', '2025-06-16 09:09:38'),
(3, 3, 'Design email integration architecture', 'Create technical design for AWS SES integration for system emails and Gmail API for agent capabilities. Include authentication flow and security considerations.', 1, 'ARCHITECT', 'PRINCIPAL', 'MAJOR', 'feature/email-integration', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:10:33', '2025-06-16 09:10:33'),
(4, 4, 'Fix remaining test isolation issues', 'Address the 2 remaining test isolation issues that are causing intermittent failures. Focus on SQLModel metadata conflicts.', 1, 'BACKEND_DEV', 'SENIOR', 'MINOR', 'fix/test-isolation', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:10:50', '2025-06-16 09:10:50'),
(5, 2, 'Create WebSocket service architecture', 'Design and implement WebSocketService class with connection management, auto-reconnect, channel subscriptions, and error handling. Create useWebSocket hook and WebSocketProvider context.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/websocket-service', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:16:25', '2025-06-16 09:16:25'),
(6, 2, 'Replace polling with WebSocket subscriptions', 'Update Dashboard, Cost Analytics, and Swarm pages to use real-time WebSocket updates instead of polling. Subscribe to swarms, costs, and system channels.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/websocket-dashboard', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:16:36', '2025-06-16 09:16:36'),
(7, 1, 'Create timeline visualization library selection', 'Research and select visualization library (D3.js, Vis.js, or Recharts) for timeline component. Create proof of concept with zoom, pan, and interactive features.', 1, 'FRONTEND_DEV', 'SENIOR', 'MINOR', 'feature/timeline-poc', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:16:46', '2025-06-16 09:16:46'),
(8, 1, 'Implement timeline page with event details', 'Create Timeline page component with route /executions/:id/timeline. Implement event list, detail panel, performance metrics, and asset lineage visualization using selected library.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/timeline-implementation', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:16:58', '2025-06-16 09:16:58'),
(9, 5, 'Implement Tasks unified view page', 'Create /tasks page showing unified workflow and swarm tasks. Include filtering, sorting, status updates, and batch operations. High priority as this is core functionality.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/tasks-page', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:17:10', '2025-06-16 09:17:10'),
(10, 5, 'Implement SwarmRuns execution page', 'Create /swarm-runs page for X-ray execution instances with timeline integration. Show active runs, execution history, and link to timeline visualization.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/swarm-runs-page', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:17:21', '2025-06-16 09:17:21'),
(11, 5, 'Complete operator dashboard pages', 'Implement remaining operator pages: PendingApprovals, InputRequired, ReviewQueue, and DecisionHistory. These are critical for human-in-the-loop functionality.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/operator-pages', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:17:31', '2025-06-16 09:17:31'),
(12, 6, 'Implement code splitting and lazy loading', 'Set up React lazy loading for route-based code splitting. Implement dynamic imports for heavy components. Target: reduce initial bundle size by 50%.', 1, 'FRONTEND_DEV', 'SENIOR', 'MAJOR', 'feature/code-splitting', 'CREATED', NULL, NULL, NULL, '2025-06-16 09:17:42', '2025-06-16 09:17:42');

-- --------------------------------------------------------

--
-- Table structure for table `taskevaluation`
--

CREATE TABLE `taskevaluation` (
  `id` int NOT NULL,
  `task_id` int NOT NULL,
  `evaluated_by` varchar(255) NOT NULL,
  `approved` tinyint(1) NOT NULL,
  `comment` text DEFAULT NULL,
  `evaluated_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `agent`
--
ALTER TABLE `agent`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_agent_agent_id` (`agent_id`);

--
-- Indexes for table `changelog`
--
ALTER TABLE `changelog`
  ADD PRIMARY KEY (`id`),
  ADD KEY `task_id` (`task_id`);

--
-- Indexes for table `document`
--
ALTER TABLE `document`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_document_doc_type` (`doc_type`),
  ADD KEY `ix_document_author_id` (`author_id`);

--
-- Indexes for table `epic`
--
ALTER TABLE `epic`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `feature`
--
ALTER TABLE `feature`
  ADD PRIMARY KEY (`id`),
  ADD KEY `epic_id` (`epic_id`);

--
-- Indexes for table `mention`
--
ALTER TABLE `mention`
  ADD PRIMARY KEY (`id`),
  ADD KEY `document_id` (`document_id`),
  ADD KEY `task_id` (`task_id`),
  ADD KEY `ix_mention_mentioned_agent_id` (`mentioned_agent_id`);

--
-- Indexes for table `service`
--
ALTER TABLE `service`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_service_service_name` (`service_name`);

--
-- Indexes for table `task`
--
ALTER TABLE `task`
  ADD PRIMARY KEY (`id`),
  ADD KEY `feature_id` (`feature_id`),
  ADD KEY `created_by_id` (`created_by_id`),
  ADD KEY `locked_by_id` (`locked_by_id`);

--
-- Indexes for table `taskevaluation`
--
ALTER TABLE `taskevaluation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `task_id` (`task_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `agent`
--
ALTER TABLE `agent`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `changelog`
--
ALTER TABLE `changelog`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `document`
--
ALTER TABLE `document`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `epic`
--
ALTER TABLE `epic`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `feature`
--
ALTER TABLE `feature`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `mention`
--
ALTER TABLE `mention`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `service`
--
ALTER TABLE `service`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `task`
--
ALTER TABLE `task`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `taskevaluation`
--
ALTER TABLE `taskevaluation`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `changelog`
--
ALTER TABLE `changelog`
  ADD CONSTRAINT `changelog_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`);

--
-- Constraints for table `feature`
--
ALTER TABLE `feature`
  ADD CONSTRAINT `feature_ibfk_1` FOREIGN KEY (`epic_id`) REFERENCES `epic` (`id`);

--
-- Constraints for table `mention`
--
ALTER TABLE `mention`
  ADD CONSTRAINT `mention_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document` (`id`),
  ADD CONSTRAINT `mention_ibfk_2` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`);

--
-- Constraints for table `task`
--
ALTER TABLE `task`
  ADD CONSTRAINT `task_ibfk_1` FOREIGN KEY (`feature_id`) REFERENCES `feature` (`id`),
  ADD CONSTRAINT `task_ibfk_2` FOREIGN KEY (`created_by_id`) REFERENCES `agent` (`id`),
  ADD CONSTRAINT `task_ibfk_3` FOREIGN KEY (`locked_by_id`) REFERENCES `agent` (`id`);

--
-- Constraints for table `taskevaluation`
--
ALTER TABLE `taskevaluation`
  ADD CONSTRAINT `taskevaluation_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
