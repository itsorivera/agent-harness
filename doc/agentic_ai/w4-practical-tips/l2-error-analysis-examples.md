# Practical Tips: Case Studies in Error Analysis

Analyzing multiple examples is essential for honing the intuition required to diagnose complex agentic workflows. These case studies illustrate how systematic error analysis prevents wasted effort on non-bottleneck components.

## Case Study 1: Invoice Processing Workflow

**Workflow**: PDF $\rightarrow$ PDF-to-Text OCR $\rightarrow$ LLM Field Extraction (Due Date, Vendor, etc.) $\rightarrow$ Database.

![Invoice Processing Workflow](/doc/assets/invoice-processing-workflow.png)
__Source:__ [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)

### The Problem:

The system frequently records incorrect "Due Dates."

### Error Analysis Methodology:

![Error Analysis Methodology](/doc/assets/error-analysis-methodology.png)
__Source:__ [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)

- **Sample Size**: Isolate 20–100 invoices with incorrect dates.
- **Diagnostic Question**: Did the OCR mangle the text, or did the LLM extract the wrong date string (e.g., the invoice date instead of the due date)?
- **Findings**:
  - OCR Errors: 10%
  - LLM Extraction Errors: **75%**
- **Action**: Focus technical effort on LLM prompting and extraction logic rather than upgrading the OCR engine.

## Case Study 2: Customer Email Automation

**Workflow**: Incoming Email $\rightarrow$ LLM Query Generation (SQL) $\rightarrow$ Database Fetch $\rightarrow$ LLM Draft Response $\rightarrow$ Human Review.

![Customer Email Automation](/doc/assets/customer-email-automation.png)
__Source:__ [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)

### The Problem:

Draft responses are often inaccurate or incomplete.

### Potential Failure Points:

![Potential Failure Points](/doc/assets/potential-failure-points.png)
__Source:__ [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)

1.  **Query Generation**: The LLM writes poor SQL (e.g., joins the wrong tables).
2.  **Data Integrity**: Output is "wrong" because the database contains corrupted or outdated data.
3.  **Drafting Logic**: The LLM has the correct data but writes a confusing or incorrect response.

### Findings:

A spreadsheet analysis reveals that **75%** of failures stem from incorrect SQL generation.

### Action Plan:

1.  **Priority 1**: Improve LLM SQL generation (few-shot prompting, schema definitions).
2.  **Priority 2**: Optimize the final drafting prompt (30% error contribution).
3.  **Deprioritize**: Database data cleaning (lowest error contribution).

## Key Takeaway: Component-Level focus

Once error analysis identifies the primary bottleneck, the next step is to implement **Component-Level Evaluations**. This allows for rapid iteration on the specific subsystem responsible for the majority of end-to-end errors.

---

_Next Topic: Implementing Component-Level Evaluations._
