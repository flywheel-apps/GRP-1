# GRP-1
Metadata Import and Validation: NON-DICOM

## Implementation

Read a given metadata file, convert to JSON, and attach to the appropriate metadata container in Flywheel:  file, subject, session etc in Flywheel database - this will be determined by the parent container. 

OPEN QUESTION 1: which container will have the metadata. If the metadata file has the same name as the input file then we may assume the metadata should be placed on that file, otherwise it should be placed on the container. 

The Goal here is to provide an example gear that reads input metadata, validates that against a template (OPEN QUESTION 2: format of template) template layout to get started - would need some indication of how to define the destination for the metatdata and template. 

### Inputs

1. metadata file
  * supports `csv` (default), `json`, AND `xlsx`

2. Json Template or Project context
  - This template should be stored as metadata on the project (provided to the gear as context input). Supports both project context and json input file (stored on the project). i.e., look for the info, and file on the project.

## Workflow

* The user uploads some data with an accompanying metadata file (envision this gear running as a rule when a .metadata file comes in)
* Read in the data - convert to json
* Read in the template from project context or trial.template.json attached to the project
* Validate metadata against the template (support regex)
* Generate error if fields are missing or invalid

_If validation errors are found:_
1. tag the container
2. log the error 
3. optionally write out error file.

### Outputs

* `.metadata.json` file containing the valid metadata that will by placed in FW, on the specified container.
* `metadata error log` (csv file with the fieldname, value (if applicable), and error (e.g., missing vs invalid)

## Other considerations

Acquisition tags are not visible in the UI presently.


