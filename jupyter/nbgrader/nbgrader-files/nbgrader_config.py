import os
c = get_config()
cwd = os.getcwd()

c.CourseDirectory.db_url = "sqlite:///{}/release/gradebook.db".format(os.getcwd())

c.ClearSolutions.code_stub = {
   "julia": "# your code here\nerror(\"Not Yet Implemented\")",
   "R": "# your code here\n.NotYetImplemented()",
   "python": "# your code here\nraise NotImplementedError",
   "javascript": "// your code here\n"
}