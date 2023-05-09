## Version
v.0.5.g
## For contributor
Setup your repo first:

```bash
# clone original repo
git clone https://github.com/awslabs/aws-ai-solution-kit.git

# checkout to aigc branch
git checkout aigc

# goto applications/stable-diffusion-extensions folder and develop on aigc branch
git add .
git commit -m "commit message"
git push origin aigc
```

### Extensions module
Install dependencies, add all new dependencies to requirements.txt:

```bash
pip install -r requirements.txt
```

### Middleware module
Deploy stack with command:

```bash
npx cdk deploy --require-approval never
```



