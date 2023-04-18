import os

# swithc to extensions directory
os.chdir("extensions/aws-ai-solution-kit")

# switch existing repo branch to aigc with force
os.system("git checkout aigc -f")
