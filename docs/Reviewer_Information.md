# Reviewer information
!!! warning "Information for reviewers only"
	The following information is for the reviewing of the EMD and some of the features descsribed may not be accessible to those not on the review team. 
	If you are interesting in helping out with the review process, please send an email to emd-submissions@wcrp-cmip.org. 
	

These are pages that provide guidance to reviewers, and anyone else interested in their submissions and how they get processsed. Not everything visible on this page will be public. 

## Useful links for users
- [Link for submitters to track their Issues](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues?q=is%3Aissue%20author%3A%40me)
- [Link for how to edit an Issue, and rerun the actions](https://scribehow.com/embed-preview/Edit_an_Issues_Description_Field_on_GitHub__BFQ9OA50Q9-RbQvQ3r_GEQ?as=slides&size=flexible)

### General rules
- IDs shall not have any underscores or spaces. Any periods "." are to be replaced with dashes "-".
- Grid descriptions should only exist to define a difference between grid cells with identical parameters, but different physical properties that cannot be documented within the current structure. 
- Links should point to permanent locations. These are Version Control Interfaces (Github, Bitbucket, GitLab etc. ) or DOI's. Users can mint a document or repository using [Zenodo](https://zenodo.org/) for free if required. 

## review procedure. 
1. (tbc) action autoassigns reviewers
2. reviewer looks at submission, Approves, or makes a suggestion. *Suggestions to be made on original issue*
3. on approval *a different* reviewer / maintainer will sanity check the submission and merge. 


## Reviewer Project Board
The reviewer project board was designed to better manage the issues and identify those relating to submissions and those which are not. 

The project board can be found at https://github.com/orgs/WCRP-CMIP/projects/8?pane=info 

It contains tabs on which issues are open, which have created pull requests for review, and which are not Form related (general issues / discussions). Additionally a tab for each form group has been provided to make it easier to locate an item. Columns for these are managed using the issue tags. 

### Post review action
Following an accepted review, an action runs to remove the `needs-review` tag from the issue, allowing the project board to move it across to the review column. Approved pull requests are denoted by a green tick next to the name on the [pull request page](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls)


Additional links to this that might be useful are: 
- [Pull requests needing review](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+-label%3Aneeds-review+review%3Anone)
- [Already reviewed pull requests in need of merging](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+-label%3Aneeds-review+review%3Aapproved)
- [Review assigned to you](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+-label%3Aneeds-review+sort%3Acreated-asc+user-review-requested%3A%40me)
- [Review assigned to you](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+-label%3Aneeds-review+sort%3Acreated-asc+user-review-requested%3A%40me)





## Using copilot as a third reviewer
If you have a copilot subscription, you will be able to allocate this as a reviewer. A comprehensive document describing what and how it will perform its review is provided in the repository.
Merits to this are: 
- greater background knowledge to confirm semantic review. 
- syntatic and grammatical suggestions
- awareness of the contents of the repository and information present on duplication. 




### Listing pull requests using the command line 
There is a tool in the main branch of the repository that allows reviewers to quickly see what pull requests are linked to which issue. 

This can be run with `git checkout main && .github/pr_issue_map.sh`

```bash
PR #86 [OPEN] — New Horizontal_computational_grid : g108-mass | tempgrid_wolfiex-1774629370
  [+] Approved : -
  [~] Engaged  : -
  └─ Issue #80 [OPEN] — New Horizontal_computational_grid : g108-mass, tempgrid_wolfiex-1774629370

PR #78 [OPEN] — New Vertical_computational_grid : tempgrid_wolfiex-1774628619
  [+] Approved : -
  [~] Engaged  : davidhassell
  └─ Issue #77 [OPEN] — New Vertical_computational_grid : tempgrid_wolfiex-1774628619
```

We can also use the `--approved` and `--needs-review` flags to filter our output as well as the `--json` flag for a more verbose output: 

```json
  {
    "pr": 78,
    "pr_title": "New Vertical_computational_grid : tempgrid_wolfiex-1774628619",
    "pr_state": "OPEN",
    "reviews": {
      "approved": "",
      "engaged": "davidhassell"
    },
    "linked_issues": [
      {
        "number": 77,
        "title": "New Vertical_computational_grid : tempgrid_wolfiex-1774628619",
        "state": "OPEN"
      }
    ]
  }
```
