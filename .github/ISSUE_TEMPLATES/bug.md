> This is the issue guide on how to write the bug reports in LamaEvents project which can be used as a template, as well.
> Remove the quoted lines that start with ">" and the titles that you do not need before you submit the issue!

## Summary

> Describe the bug under this section. It should answer questions like "_How the bug occurred?_", 
> "_It occurred after which steps were taken?_", "_How the other people could reproduce it?_" etc.

**Error:**
> If there was an error message, please place it here in a code block. See the example below.
```
Traceback:
  File 'brain.py', node 42,:
    make_up(error_message)
Error 404: error_message not found
```

> If possible, give the URL that generates the error as shown below

**URL that generates the error:** {{ url_generates_error }}

## Possible Problems

> If you can not be sure what actually caused the bug but you have ideas on it, list them under this section.  
> Listed problems are going to be investigated and when the actual cause is found, the solution should be elaborated under the section _Solution_. 
> See the examples below.
* {{ First idea on the bug }}
* {{ Second idea on the bug }}

## Solution

> If you discover what actually caused this bug and know how to solve it, elaborate on your solution under this section. 

## Steps

> List the steps that should be taken to solve the bug. It can be about technical coding steps or more general. 
> It is important to list the steps with checkboxes. Example use on checkboxes is shown below.
- [ ] {{ first_task }}
- [ ] {{ second_task }}
