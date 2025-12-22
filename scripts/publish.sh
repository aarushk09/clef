#!/bin/bash

# EdPear Publishing Script
# This script helps you publish the combined SDK and CLI package to npm

set -e  # Exit on error

echo "🚀 EdPear Publishing Script"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if logged in to npm
if ! npm whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged in to npm${NC}"
    echo "Please run: npm login"
    exit 1
fi

echo -e "${GREEN}✅ Logged in as: $(npm whoami)${NC}"
echo ""

echo -e "${YELLOW}Publishing the combined SDK and CLI (@edpear/sdk)...${NC}"

cd edpear-sdk
npm run build
npm publish --access public

echo ""
echo -e "${GREEN}🎉 Publishing complete!${NC}"
echo ""
echo "Verify at:"
echo "  SDK: https://www.npmjs.com/package/@edpear/sdk"
