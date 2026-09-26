SEC EDGAR 10-K Data Automation Service

Project Overview

As part of the Data Automation assignment, I designed and implemented a Python-based service to automatically retrieve the latest 10-K filings for six publicly traded companies from the SEC EDGAR API, convert the filings into PDF documents, and generate structured metadata for downstream use.

The companies selected for the implementation were Apple, Meta, Alphabet, Amazon, Netflix, and Goldman Sachs.

The solution was designed using a modular architecture so that each part of the workflow could be maintained independently and extended in the future. The overall objective was to create a reliable pipeline that could retrieve filing data, process the documents, and make the resulting information available for use by other teams or services.

 1. Solution Architecture

The project was structured into separate Python modules for configuration, SEC API communication, PDF conversion, and workflow orchestration.

The config.py file contains the company configuration, SEC User-Agent settings, and output configuration. The sec_client.py module is responsible for communicating with the SEC EDGAR endpoints, retrieving company CIK numbers, and identifying the latest 10-K filing. The pdf_converter.py module handles the conversion of the downloaded filing HTML into a PDF document.

The main.py file coordinates the complete workflow for all six companies and generates the final output. A summary.json file is also created to store important filing metadata that can be consumed by downstream applications or other teams. The project also includes a README.md file containing setup and execution instructions and a requirements.txt file containing the required Python dependencies.

The overall processing flow is company ticker lookup, CIK identification, filing history retrieval, latest 10-K selection, HTML download, PDF conversion, and metadata generation.

2. SEC EDGAR API Integration

The service uses the SEC's public EDGAR endpoints to retrieve company and filing information.

The first endpoint is used to map company tickers to their corresponding SEC Central Index Key, or CIK. The CIK is then used to access the company's filing history through the SEC submissions endpoint.

From the filing history, the implementation filters the available records based on the form type and selects the most recent filing with the form type 10-K using the filing date.

For every selected filing, the service captures the company name, CIK, filing type, filing date, accession number, and source filing URL.

A compliant SEC User-Agent was also configured for the requests in accordance with the SEC's fair-access requirements.

 3. PDF Conversion

The initial implementation used WeasyPrint to convert the SEC filing HTML into PDF format.

During local testing on Windows, WeasyPrint encountered issues with system-level dependencies related to Pango and GTK libraries. Since these dependencies introduced additional installation and configuration requirements, I evaluated an alternative PDF rendering approach.

I replaced WeasyPrint with Playwright and headless Chromium. This provided a more reliable browser-based rendering solution and avoided the system-level dependency problems encountered with the initial implementation.

4. Handling SEC Automated-Traffic Restrictions

During testing, I encountered another issue when Playwright attempted to access the SEC filing URL directly.

Although the requests included the required User-Agent, direct browser navigation to the SEC document was detected by the SEC's automated-traffic protection and the request was blocked.

To resolve this, I separated the document retrieval process from the PDF rendering process.

The final implementation first downloads the filing HTML using Python requests. The downloaded HTML is then stored locally, after which Playwright opens the local file and uses headless Chromium to render it as a PDF.

This means that the browser does not make a direct request to the SEC server. It only processes the locally downloaded document. Separating these two stages also resulted in a cleaner architecture where data retrieval and document rendering are handled independently.

 5. Validation and Verification

After completing the implementation, I validated the generated results against the public filing records available through SEC EDGAR.

For each company, I verified that the selected document was a 10-K and that the filing date and accession number matched the corresponding SEC filing record. I also verified that the generated source URL pointed to the expected filing.

The generated PDF files were checked for page count, embedded text, and the presence of the expected SEC Form 10-K cover page. I also verified that the company name and SEC commission file number were correctly displayed.

These checks helped confirm that the pipeline was generating the actual filing documents rather than partial downloads, access-denied pages, or other error responses.

 6. Final Results

The complete pipeline successfully processed all six companies: Apple, Meta, Alphabet, Amazon, Netflix, and Goldman Sachs.

The resulting PDF documents varied in length depending on the company's filing. The generated files ranged from approximately 61 pages for Apple to 292 pages for Goldman Sachs.

The summary.json file was also cross-checked against SEC EDGAR's filing records to confirm that the metadata corresponded to the correct filings.

7. Technical Challenges and Resolution

One of the main challenges was the PDF conversion dependency on Windows. The initial WeasyPrint implementation required Pango and GTK libraries, which caused installation and runtime issues. This was resolved by replacing WeasyPrint with Playwright and Chromium.

Another challenge was the SEC's automated-traffic protection. Direct navigation to SEC documents through Playwright resulted in blocked requests. I resolved this by downloading the filing through Python requests first and then using Playwright only for local PDF rendering.

Another important part of the implementation was ensuring that the correct filing was selected. Since companies have multiple historical 10-K filings, the application filters the SEC filing history by form type and selects the most recent filing based on its filing date.

The final challenge was making the retrieved information available for downstream use. To address this, the service generates a structured summary.json file containing the key filing metadata, allowing other applications or teams to consume the information without having to process the SEC filing themselves.

 8. Technologies Used

The project was implemented using Python and the SEC EDGAR API. Python Requests was used for HTTP communication and data retrieval, while Playwright and Chromium were used for HTML rendering and PDF generation. JSON was used for structured metadata, and Git was used for source-code version control.

 9. Conclusion

The completed solution successfully automates the process of identifying and retrieving the latest 10-K filing for the six selected companies, downloading the filing content, converting it into PDF format, and generating structured metadata for downstream consumption.

The implementation also provided practical experience in REST API integration, document processing, browser automation, dependency management, debugging, data validation, and designing a modular Python service.

The final pipeline provides a reusable foundation that can be extended to support additional companies, different SEC filing types, or further downstream data-processing and analytics workflows.
