import os,re,json,sys
import shutil

# Process all the files
if __name__ == "__main__":
	print("Redaction functionality is removed for coursera-labs image for academic integrity purposes.")
	shutil.copyfile(sys.argv[1], sys.argv[1]+'.clean')

