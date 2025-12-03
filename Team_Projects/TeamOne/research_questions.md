# Research Questions

This document outlines the key research questions for our analysis of job creation and firm performance indicators.

## Research Questions

### 1. Job Creation Model
**Question:** What factors predict job creation?

**Model Specification:**
```
Job creation = B₀ + B₁(size_num) + B₂(credit_line) + B₃(certification) + ...
```

**Answer:**

Key factors that predict job creation include:

- **Company Size:**
  - **On absolute terms:** Large companies create the most jobs; regardless of country, larger companies naturally create more jobs.
  - **On size-adjusted terms:** Medium companies create the most jobs relative to their size.

- **Access to Credit:** Access to credit for firms is a significant indicator of ability to create jobs.

- **Certification:** Firms having Certification of Quality standards are associated with job creation.

- **Interest Rates:** Firms that indicated interest rates were unfavorable also saw a decrease in employment.

---

### 2. Firm Maturity and Job Creation
**Question:** How does the maturity of firms affect jobs, even if other indicators are positive?

**Answer:**

There is a negative correlation with the maturity of the firm. Newer firms created more jobs. Specifically, younger medium companies create more jobs than mature/old companies, even when controlling for other positive indicators.

---

### 3. Access to Credit and Job Creation
**Question:** How does access to credit impact companies' abilities to create jobs?

**Answer:**

Access to credit for firms is a significant indication of ability to create jobs. Firms with better access to credit are more capable of expanding operations and creating employment opportunities.

---

### 4. Interest Rates and Job Creation
**Question:** What is the relationship between favorable interest rates (as indicated by firms) and job creation?

**Answer:**

Firms that indicated interest rates were unfavorable also saw a decrease in employment. This suggests that favorable interest rates (or at least the perception of favorable rates) are associated with job creation, while unfavorable rates are associated with employment declines.

---

### 5. Industry Employment Across Countries
**Question:** Is industry employment correlated (negatively) across countries?

**Answer:**
_To be completed_

---

### 6. Regulatory Burden and Gender
**Question:** Does the same regulatory burden (time spent with officials) hurt female-led firms more than male-led firms?

**Answer:**
_To be completed_

---

### 7. Management Quality vs. Access to Finance
**Question:** Is Management Quality (targets, monitoring) a stronger predictor of growth than Access to Finance?

**Answer:**
_To be completed_

---

## Notes

- All analyses will be conducted using the joined dataset created from the ES-Indicators Database and New Comprehensive datasets
- The datasets are linked via the `idstd` column
- Results will be documented with statistical tests, visualizations, and interpretations

