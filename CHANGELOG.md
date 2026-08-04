# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_Any upcoming features or bug fixes currently being worked on will be listed here._

## [0.1.3] - 2026-08-04

### Added

- **Core Engine:** Blazing fast, vectorized mock data generation using `numpy` and `asyncio`.
- **Two-Tier Architecture:** Bypassed PyPI's 100MB limit by implementing an auto-downloader that fetches heavy locale JSONs from GitHub Releases dynamically.
- **CSV Streaming:** Added `to_csv()` method for high-performance streaming to disk without overloading RAM.
- **Async Batching:** Added `generate_batches()` method to yield data chunks for non-blocking database seeding (e.g., `asyncpg`, `aiosqlite`).
- **Typo Protection:** Implemented fuzzy matching to actively suggest correct provider names when a user makes a typo (e.g., suggesting `color_name` for `colr`).
- **DX Methods:** Added `get_providers()` and `available_locales()` helper methods to allow developers to explore datasets without reading source code.
- **Benchmarking Suite:** Added a reproducible benchmark script (`benchmarks/run_benchmarks.py`) that profiles execution time, memory usage, and generates visual charts.
- **CI/CD:** Configured GitHub Actions workflows for locale packing, linting (`ruff`), and testing (`pytest`).

### Changed

- Refactored repository structure to isolate internal scripts (`scripts/`), user examples (`examples/`), and performance tests (`benchmarks/`).
- Migrated configuration fully to `pyproject.toml`.

### Fixed

- Modernized NumPy RNG seeding to ensure zero ID collisions when generating 100k+ records.
- Fixed package data configuration in `MANIFEST.in` to properly include locale JSON files in PyPI builds.
