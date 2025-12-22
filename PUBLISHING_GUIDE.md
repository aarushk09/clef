# Publishing Guide for EdPear Libraries

This guide will walk you through publishing the EdPear CLI and SDK to npm.

## Prerequisites

1. **npm Account**: Create an account at [npmjs.com](https://www.npmjs.com/signup)
2. **Organization Setup** (Recommended): Create an organization named `@edpear` on npm
3. **Authentication**: Login to npm from your terminal

## Step 1: Setup npm Account

### Create npm Account
1. Go to [npmjs.com/signup](https://www.npmjs.com/signup)
2. Create your account
3. Verify your email

### Create Organization (Recommended)
1. Go to [npmjs.com/org/create](https://www.npmjs.com/org/create)
2. Create organization: `@edpear`
3. This allows you to publish scoped packages like `@edpear/cli` and `@edpear/sdk`

### Login to npm
```bash
npm login
```
Enter your username, password, and email when prompted.

## Step 2: Prepare Packages for Publishing

### Update Package Metadata

Before publishing, update the package.json files with:
- Repository URL
- Homepage
- Bug reports URL
- Author information

### Build the Packages

Both packages need to be built before publishing:

```bash
# Build CLI
cd edpear-cli
npm install
npm run build

# Build SDK
cd ../edpear-sdk
npm install
npm run build
```

## Step 3: Publish CLI Package

### Navigate to CLI Directory
```bash
cd edpear-cli
```

### Test Build
```bash
npm run build
```

Verify that the `dist/` folder contains:
- `index.js`
- `index.d.ts` (if TypeScript declarations are generated)

### Check Package Contents
```bash
npm pack
```

This creates a `.tgz` file. You can inspect it to see what will be published.

### Publish
```bash
npm publish --access public
```

The `--access public` flag is required for scoped packages (`@edpear/cli`).

**First Time Publishing:**
- Package will be published as `@edpear/cli@1.0.0`
- Make sure the version in `package.json` is correct

## Step 4: Publish SDK Package

### Navigate to SDK Directory
```bash
cd edpear-sdk
```

### Test Build
```bash
npm run build
```

### Publish
```bash
npm publish --access public
```

## Step 5: Verify Publication

### Check on npm Website
1. Visit: `https://www.npmjs.com/package/@edpear/cli`
2. Visit: `https://www.npmjs.com/package/@edpear/sdk`

### Test Installation
```bash
# Test CLI installation
npm install -g @edpear/cli
edpear --version

# Test SDK installation
npm install @edpear/sdk
```

## Step 6: Update API URLs

Before publishing, make sure to update the default API URLs in the packages:

### CLI (`edpear-cli/src/index.ts`)
Update the base URL:
```typescript
const baseURL = process.env.EDPEAR_API_URL || 'https://api.edpear.com';
```

### SDK (`edpear-sdk/src/index.ts`)
Update the base URL:
```typescript
this.baseURL = config.baseURL || 'https://api.edpear.com';
```

## Versioning Strategy

### Semantic Versioning
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Update Version
```bash
# In package.json, update version manually or use:
npm version patch  # 1.0.0 → 1.0.1
npm version minor # 1.0.0 → 1.1.0
npm version major # 1.0.0 → 2.0.0
```

### Publishing Updates
After updating version:
```bash
npm run build
npm publish --access public
```

## Publishing Checklist

Before publishing, ensure:

- [ ] All code is tested and working
- [ ] `package.json` has correct metadata
- [ ] `README.md` is complete and accurate
- [ ] `.npmignore` or `files` field excludes unnecessary files
- [ ] TypeScript builds successfully
- [ ] API URLs point to production (not localhost)
- [ ] Version number is correct
- [ ] License is specified
- [ ] Repository URL is set (if public)

## Common Issues

### Issue: "You do not have permission to publish"
**Solution**: 
- Make sure you're logged in: `npm whoami`
- For scoped packages, use `--access public`
- Check if the package name is already taken

### Issue: "Package name already exists"
**Solution**:
- Choose a different name
- Or contact the owner of the existing package

### Issue: "Invalid package name"
**Solution**:
- Package names must be lowercase
- Scoped packages must start with `@`
- No spaces or special characters (except `-` and `_`)

### Issue: "Missing files"
**Solution**:
- Check the `files` field in `package.json`
- Ensure `dist/` folder exists after build
- Verify `prepublishOnly` script runs build

## Automated Publishing (Optional)

### Using GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to npm

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'
      - run: cd edpear-cli && npm ci && npm run build && npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{secrets.NPM_TOKEN}}
      - run: cd edpear-sdk && npm ci && npm run build && npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{secrets.NPM_TOKEN}}
```

## Post-Publishing

### Announce the Release
- Update your website
- Post on social media
- Update documentation
- Notify users if applicable

### Monitor Usage
- Check npm download statistics
- Monitor for issues
- Gather user feedback

## Quick Reference

```bash
# Login to npm
npm login

# Build and publish CLI
cd edpear-cli
npm run build
npm publish --access public

# Build and publish SDK
cd ../edpear-sdk
npm run build
npm publish --access public

# Update version and publish
npm version patch
npm run build
npm publish --access public
```

## Next Steps

After publishing:
1. Test installation from npm
2. Update your website with installation instructions
3. Create release notes
4. Monitor for any issues
5. Plan for future updates

---

**Need Help?**
- npm Documentation: https://docs.npmjs.com/
- npm Support: https://www.npmjs.com/support
