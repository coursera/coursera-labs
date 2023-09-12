import os
c = get_config()
cwd = os.getcwd()

c.CourseDirectory.course_id = "cs617"
c.Exchange.root = "/usr/local/share/nbgrader/exchange"

c.CourseDirectory.db_url = "sqlite:///{}/release/gradebook.db".format(os.getcwd())

c.ClearSolutions.code_stub = {
   "julia": "# your code here\n",
   "R": "# your code here\n",
   "python": "# your code here\n",
   "javascript": "// your code here\n"
}

