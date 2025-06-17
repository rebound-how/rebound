# Rem Improvement Suggestions

Generate a GNU‐style unified diff that transforms the **original** implementation of this {lang} function into a **more reliable** version achieving at least a reliability score of {target_score}.  

* Score scale goes from 0.0 (very bad) to 1.0 (very good).
* Code must be professional and readable.
* If not smart changes can be offered, return an empty response.
* Do NOT change the behavior of the code.
* Assume function arguments have been validated and correct.
* If the function is missing a docstring, add a comprehensive one.
* Do not include any explanation - output only the diff:

--- original
{snippet}

+++ improved
