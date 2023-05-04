<<<<<<< HEAD
import launch
import os

req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "scripts", "requirements.txt")

with open(req_file) as file:
    for lib in file:
        lib = lib.strip()
        if not launch.is_installed(lib):
            launch.run_pip(f"install {lib}", f"sd-webui-sagemaker requirement: {lib}")
=======
import os

# swithc to extensions directory
os.chdir("extensions/aws-ai-solution-kit")

# switch existing repo branch to aigc with force
os.system("git checkout aigc -f")
>>>>>>> af994859d39f30bea0487e84fac3c06bc20740a3
