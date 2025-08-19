[![Tests](https://github.com/Abeelha/ckanext-onboarding-theodoro-bertol/workflows/Tests/badge.svg?branch=main)](https://github.com/Abeelha/ckanext-onboarding-theodoro-bertol/actions)

# ckanext-onboarding-theodoro-bertol

A CKAN extension that implements a dataset review workflow where new datasets require approval before becoming public. This extension provides a complete review system with reviewer management, visual status indicators, and automated privacy control.


## Features

- **Automatic Review Workflow**: New datasets are automatically set to "pending" review status and remain private
- **Reviewer Management**: Administrators can grant/revoke reviewer permissions to users
- **Review Actions**: Reviewers can approve or reject datasets through the web interface
- **Visual Status Indicators**: Review status badges appear on dataset pages and listings
- **Privacy Control**: Approved datasets automatically become public, rejected datasets remain private

## Requirements

- CKAN 2.10+
- Python 3.8+

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.10            | yes           |
| 2.9             | not tested    |
| 2.8             | not tested    |
| 2.7 and earlier | not tested    |


## Installation

To install ckanext-onboarding-theodoro-bertol:

1. Activate your CKAN virtual environment, for example:

```bash
. /usr/lib/ckan/default/bin/activate
```

2. Clone the source and install it on the virtualenv

```bash
git clone https://github.com/Abeelha/ckanext-onboarding-theodoro-bertol.git
cd ckanext-onboarding-theodoro-bertol
pip install -e .
pip install -r requirements.txt
```

3. Add `onboarding_theodoro_bertol` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

```bash
sudo service apache2 reload
```


## Configuration

No additional configuration is required. The extension works out of the box.

## Usage

### For Administrators

1. **Managing Reviewers**: 
   - Navigate to `/ckan-admin/reviewers`
   - Grant or revoke reviewer permissions to users
   - Sysadmins automatically have reviewer permissions

### For Reviewers

1. **Reviewing Datasets**:
   - Navigate to any dataset with "pending" status
   - Use the "Approve" or "Reject" buttons to review the dataset
   - Approved datasets become public automatically
   - Rejected datasets remain private and can be edited by the owner

### For Dataset Creators

1. **Creating Datasets**:
   - Create datasets as normal
   - New datasets are automatically set to "pending" review
   - Datasets remain private until approved
   - If rejected, edit your dataset and it will be resubmitted for review

## API Actions

The extension provides the following API actions:

- `dataset_review`: Approve or reject a dataset (reviewers only)
- `user_reviewer_grant`: Grant reviewer permissions to a user (sysadmins only)
- `user_reviewer_revoke`: Revoke reviewer permissions from a user (sysadmins only)

### Example API Calls

```bash
# Approve a dataset
curl -X POST http://localhost:5000/api/3/action/dataset_review \
  -H "Authorization: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id": "dataset-id", "review_status": "approved"}'

# Grant reviewer permission
curl -X POST http://localhost:5000/api/3/action/user_reviewer_grant \
  -H "Authorization: SYSADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-id"}'
```


## Developer installation

To install ckanext-onboarding-theodoro-bertol for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/Abeelha/ckanext-onboarding-theodoro-bertol.git
    cd ckanext-onboarding-theodoro-bertol
    pip install -e .
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## Releasing a new version of ckanext-onboarding-theodoro-bertol

If ckanext-onboarding-theodoro-bertol should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `pyproject.toml` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python -m build && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
