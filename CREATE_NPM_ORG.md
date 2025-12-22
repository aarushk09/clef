# Creating @edpear Organization on npm

## Option 1: Create Organization (Recommended)

### Step 1: Go to npm Organization Page
1. Visit: https://www.npmjs.com/org/create
2. Or go to: https://www.npmjs.com → Click your profile → "Add Organization"

### Step 2: Create Organization
1. Enter organization name: **edpear**
2. Choose plan (Free plan is fine for now)
3. Click "Create Organization"

### Step 3: Verify
- You should now see `@edpear` in your organizations list
- The organization is ready to publish packages

### Step 4: Publish Again
```bash
cd edpear-cli
npm publish --access public
```

## Option 2: Publish Under Personal Account

If you don't want to create an organization, you can publish under your personal account:

### Change Package Names

**For CLI (`edpear-cli/package.json`):**
```json
{
  "name": "edpear-cli",  // Remove @edpear/ prefix
  ...
}
```

**For SDK (`edpear-sdk/package.json`):**
```json
{
  "name": "edpear-sdk",  // Remove @edpear/ prefix
  ...
}
```

### Then Publish
```bash
npm publish  # No --access public needed for unscoped packages
```

**Note:** Users would install as:
- `npm install -g edpear-cli` (instead of `@edpear/cli`)
- `npm install edpear-sdk` (instead of `@edpear/sdk`)

## Option 3: Use Your Username as Scope

If your npm username is different, you can use it:

**For CLI (`edpear-cli/package.json`):**
```json
{
  "name": "@your-username/edpear-cli",
  ...
}
```

**For SDK (`edpear-sdk/package.json`):**
```json
{
  "name": "@your-username/edpear-sdk",
  ...
}
```

Then publish with:
```bash
npm publish --access public
```

## Recommendation

**I recommend Option 1** (creating the organization) because:
- ✅ Professional appearance (`@edpear/cli` looks better)
- ✅ Can add team members later
- ✅ Better for branding
- ✅ Free for public packages
- ✅ Matches your existing package.json setup

## Quick Steps to Create Organization

1. Go to: https://www.npmjs.com/org/create
2. Enter: **edpear**
3. Click "Create Organization"
4. Wait a few seconds for it to be created
5. Run: `npm publish --access public` again

That's it! The organization creation is instant and free for public packages.
