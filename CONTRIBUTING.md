# Contributing to the Data Engineering Playbook

We welcome contributions from the community! Whether you're adding a new template, improving docs, fixing bugs, or sharing a case study, your help makes this resource better for everyone.

## How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/baseline0/data-engineering-playbook.git
cd data-engineering-playbook
```

### 2. Create a Branch
```bash
git checkout -b feature/your-contribution-name
```

### 3. Make Changes

#### Adding a New Template
- Create `templates/your_template/` with:
  - `README.md` — Explains the pattern
  - `diagram.md` — Architecture diagram (ASCII or Mermaid)
  - `example/` — Minimal working code
  - `costs.md` — Cost breakdown
  - `tradeoffs.md` — When to use/not use

#### Adding a Case Study
- Create `case_studies/your_domain/` with:
  - `README.md` — Overview and results
  - `data/` — Sample data or fetch scripts
  - `dbt/` — dbt project (if applicable)
  - `scripts/` — Python scripts for ingestion/processing
  - `tests/` — Great Expectations validation
  - `api/` — REST endpoint code (if applicable)

#### Improving Documentation
- Edit files in `docs/`
- Keep language clear and example-driven
- Link to working code when possible

### 4. Test Your Changes
```bash
# For case studies: verify scripts run
cd case_studies/your_study
python scripts/fetch_data.py
dbt run

# For templates: verify example code works
cd templates/your_template/example
# Run setup/validation steps
```

### 5. Commit & Push
```bash
git add .
git commit -m "Add: your contribution description"
git push origin feature/your-contribution-name
```

### 6. Create a Pull Request
- Describe what you added and why
- Link to any relevant issues
- Mention if this is a new template, case study, or doc improvement

## Guidelines

### Code Style
- **Python**: Follow PEP 8, use type hints
- **SQL/dbt**: Use consistent casing (lowercase for objects, UPPERCASE for keywords)
- **YAML**: Use 2-space indentation

### Documentation
- Be clear and concise
- Include working examples
- Explain the "why", not just the "what"
- Add comments to non-obvious code

### Attribution
- If you use external resources, cite them
- Link to original projects and authors
- Include relevant licenses

### Keep It Real
- This playbook is about practical, proven patterns
- Avoid theoretical concepts without real examples
- Be honest about limitations and trade-offs

## What We're Looking For

### High Priority
- ✅ New templates (common patterns)
- ✅ Case studies (real data, real problems)
- ✅ Improvements to existing docs
- ✅ Bug fixes and clarifications

### Lower Priority
- ❌ Marketing/promotional content
- ❌ Tools that require paid services
- ❌ Patterns specific to one expensive platform
- ❌ Theoretical discussions without code

## Questions?

- Open an **issue** to discuss ideas first
- See `README.md` for context on the playbook's philosophy
- Check existing templates to see the pattern

---

**Thank you for contributing!** This resource is built by the community, for the community.
