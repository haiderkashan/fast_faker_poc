# Contributing to Async Batch Faker

First off, thank you for considering contributing to `async-batch-faker`!

Our goal is to be the absolute fastest mock data generator in the Python ecosystem. Whether you are fixing a bug, adding a new localization, or optimizing the NumPy vectorization further, your help is deeply appreciated.

## 🧠 The Architecture (Before You Code)

Unlike standard Faker, this library operates on a **Two-Tier Architecture**:

1. **Core Engine (`src/`)**: The fast, async, NumPy-powered generator.
2. **Dynamic Locales (`scripts/`)**: We keep the PyPI package lightweight. Massive localization JSONs are packed using internal scripts and fetched on-demand via GitHub releases.

If you are modifying how datasets are structured, check out the tools in the `scripts/` directory first.

## 🛠️ Local Development Setup

To set up the project locally for development, follow these steps:

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/async-batch-faker.git
   cd async-batch-faker
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On macOS/Linux: source venv/bin/activate
   ```

3. **Install the package in editable mode with dev dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```
   _(If your pyproject.toml doesn't have a `[dev]` tag yet, just run `pip install -e . pytest ruff matplotlib`)_

## 🧪 Code Quality: Linting & Testing

We use Ruff for lightning-fast linting and formatting, and Pytest for our test suite. Before submitting any code, you must ensure it passes both.

**Format your code:**

```bash
ruff format .
```

**Run the linter:**

```bash
ruff check . --fix
```

**Run the test suite:**

```bash
pytest
```

Ensure all tests pass. If you are adding a new feature, please write a test for it in the `tests/` directory.

## 🚀 The Golden Rule: Benchmarking

Speed is the core feature of this library. No Pull Request will be merged if it degrades performance.

If you modify the core generation engine in `src/`, you must run the benchmark suite against your changes:

```bash
python benchmarks/run_benchmarks.py
```

Please include the generated Markdown table and a brief explanation of any performance changes in your Pull Request description.

## 📝 Submitting a Pull Request

1. Create a new branch for your feature or bugfix (`git checkout -b feature/add-new-provider`).
2. Make your changes and ensure they pass `ruff` and `pytest`.
3. Commit your changes with clear, descriptive commit messages.
4. Push your branch to your fork (`git push origin feature/add-new-provider`).
5. Open a Pull Request on the main repository.

We will review your PR as quickly as possible. Thanks for helping make Python database seeding faster for everyone!
