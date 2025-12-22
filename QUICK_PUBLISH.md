# Quick Publishing Guide

## Prerequisites Checklist

- [ ] npm account created at [npmjs.com](https://www.npmjs.com/signup)
- [ ] Organization `@edpear` created (optional but recommended)
- [ ] Logged in: `npm login`
- [ ] Production API deployed and accessible
- [ ] Repository URLs updated in package.json files

## Quick Start (5 Steps)

### 1. Login to npm
```bash
npm login
```

### 2. Build and Publish CLI
```bash
cd edpear-cli
npm install
npm run build
npm publish --access public
```

### 3. Build and Publish SDK
```bash
cd ../edpear-sdk
npm install
npm run build
npm publish --access public
```

### 4. Verify Publication
Visit:
- https://www.npmjs.com/package/@edpear/cli
- https://www.npmjs.com/package/@edpear/sdk

### 5. Test Installation
```bash
# Test CLI
npm install -g @edpear/cli
edpear --version

# Test SDK
npm install @edpear/sdk
```

## Using the Publishing Scripts

### Windows (PowerShell)
```powershell
.\scripts\publish.ps1
```

### Mac/Linux (Bash)
```bash
chmod +x scripts/publish.sh
./scripts/publish.sh
```

## Important Notes

1. **API URLs**: Both packages now default to production URLs:
   - CLI: `https://api.edpear.com` (can override with `EDPEAR_API_URL` env var)
   - SDK: `https://api.edpear.com` (can override in config)

2. **Version Updates**: When updating packages:
   ```bash
   # Update version in package.json, then:
   npm run build
   npm publish --access public
   ```

3. **Scoped Packages**: The `--access public` flag is required for scoped packages like `@edpear/cli`

4. **First Time**: Make sure you have:
   - Created the `@edpear` organization on npm (or use your personal account)
   - Verified your email address
   - Set up 2FA (recommended)

## Troubleshooting

**"You do not have permission"**
- Make sure you're logged in: `npm whoami`
- For scoped packages, ensure you're a member of the `@edpear` organization

**"Package name already exists"**
- The package name is already taken
- Check if you own it or need to use a different name

**Build fails**
- Make sure TypeScript is installed: `npm install`
- Check for TypeScript errors: `npm run build`

## After Publishing

1. Update your website with installation instructions
2. Create a GitHub release
3. Announce on social media
4. Monitor npm download stats
5. Gather user feedback

---

For detailed information, see [PUBLISHING_GUIDE.md](./PUBLISHING_GUIDE.md)
