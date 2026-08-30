<h1 align="center">
  <br>
  <a href="https://github.com/BrendenWalker/TandoorNG"><img src="docs/logo_color.svg" height="256px" width="256px"></a>
  <br>
  Stillroom
  <br>
</h1>

<h4 align="center">The recipe manager that allows you to manage your ever growing collection of digital recipes.</h4>

<p align="center">
<a href="https://github.com/BrendenWalker/TandoorNG/actions" target="_blank" rel="noopener noreferrer"><img src="https://github.com/BrendenWalker/TandoorNG/workflows/Continuous%20Integration/badge.svg?branch=develop" ></a>
<a href="https://github.com/BrendenWalker/TandoorNG/stargazers" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/github/stars/BrendenWalker/TandoorNG" ></a>
<a href="https://github.com/BrendenWalker/TandoorNG/releases/latest" rel="noopener noreferrer"><img src="https://img.shields.io/github/v/release/BrendenWalker/TandoorNG" ></a>
</p>

<p align="center">
<a href="https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/install/docker.md" target="_blank" rel="noopener noreferrer">Installation</a> •
<a href="https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/index.md" target="_blank" rel="noopener noreferrer">Docs</a> •
<a href="https://github.com/BrendenWalker/TandoorNG/issues" target="_blank" rel="noopener noreferrer">Issues</a>
</p>

![Preview](docs/preview.png)

## Core Features

- Manage your recipes - Manage your ever growing recipe collection
- Plan - multiple meals for each day
- Shopping lists - via the meal plan or straight from recipes
- Use AI to recognize images, sort recipe steps, find nutrition facts and more
- Cookbooks - collect recipes into books
- Share and collaborate on recipes with friends and family

## Made by and for power users

- Powerful and customizable search with fulltext support and [TrigramSimilarity](https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/#trigram-similarity)
- Create and search for tags, assign them in batch to all files matching certain filters
- Quickly merge and rename ingredients, tags and units
- Import recipes from thousands of websites supporting [ld+json or microdata](https://schema.org/Recipe)
- Support for fractions or decimals
- Easy setup with Docker and included examples for Kubernetes
- Customize your interface with themes
- Sync files with Dropbox and Nextcloud

## All the must haves

- Optimized for use on mobile devices
- Localized in many languages thanks to the awesome community
- Import your collection from many other [recipe managers](docs/features/import_export.md)
- Many more like recipe scaling, image compression, printing views and supermarkets

This application is meant for people with a collection of recipes they want to share with family and friends or simply
store them in a nicely organized way. A basic permission system exists but this application is not meant to be run as
a public page.

Stillroom is an independent fork of [Tandoor Recipes](https://github.com/TandoorRecipes/recipes).

## Docs

Documentation lives in [`docs/`](docs/index.md). Docker install instructions are in [`docs/install/docker.md`](docs/install/docker.md).

The published image is `ghcr.io/brendenwalker/stillroom`.

## Migrating from Tandoor

Move recipes with Tandoor's **Default** export, then Stillroom's **Default** import. That format includes images.

1. In Tandoor, export using the **Default** format (Import/Export).
2. Install Stillroom. Docker instructions are in [`docs/install/docker.md`](docs/install/docker.md).
3. In Stillroom, import the same file with **Default**.

This copies recipes, images, and related recipe data. It does not copy accounts, meal plans, shopping lists, or server settings. Recreate users as needed, and re-add the import bookmarklet from Stillroom's import page if you used Tandoor's.

## Contributing

Contributions are welcome. Please read [the contribution guidelines](docs/contribute/guidelines.md) before opening a pull request.

There is no contributor license agreement. A pull request licenses your contribution under the same terms as this repository. You keep your copyright.

## License

Beginning with version 0.10.0 the code in this repository is licensed under the [GNU AGPL v3](https://www.gnu.org/licenses/agpl-3.0.de.html) license with a
[common clause](https://commonsclause.com/) selling exception. See [LICENSE.md](LICENSE.md) for details.
