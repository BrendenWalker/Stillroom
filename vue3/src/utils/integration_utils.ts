

export type Integration = {
    id: string,
    name: string,
    import: boolean,
    export: boolean,
    helpUrl: string,
    imgSrc?: string,
}

export const INTEGRATIONS: Array<Integration> = [
    {id: 'DEFAULT', name: "Stillroom", import: true, export: true, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#default', imgSrc: 'https://raw.githubusercontent.com/BrendenWalker/TandoorNG/develop/docs/logo_color.svg'},
    {id: 'CHEFTAP', name: "Cheftap", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#cheftap'},
    {id: 'CHOWDOWN', name: "Chowdown", import: true, export: true, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#chowdown'},
    {id: 'COOKBOOKAPP', name: "CookBookApp", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#cookbookapp'},
    {id: 'COOKLANG', name: "Cooklang Markdown", import: true, export: true, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#cooklang'},
    {id: 'COOKMATE', name: "Cookmate", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#cookmate'},
    {id: 'COPYMETHAT', name: "CopyMeThat", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#copymethat'},
    {id: 'DOMESTICA', name: "Domestica", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#domestica'},
    {id: 'MEALIE', name: "Mealie 0.x", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#mealie'},
    {id: 'MEALIE1', name: "Mealie 1.x", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#mealie'},
    {id: 'MEALMASTER', name: "Mealmaster", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#mealmaster'},
    {id: 'MELARECIPES', name: "Melarecipes", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#melarecipes'},
    {id: 'NEXTCLOUD', name: "Nextcloud Cookbook", import: true, export: true, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#nextcloud'},
    {id: 'OPENEATS', name: "Openeats", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#openeats'},
    {id: 'PAPRIKA', name: "Paprika", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#paprika'},
    {id: 'PEPPERPLATE', name: "Pepperplate", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#pepperplate'},
    {id: 'PLANTOEAT', name: "Plantoeat", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#plantoeat'},
    {id: 'RECETTETEK', name: "RecetteTek", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#recettetek'},
    {id: 'RECIPEKEEPER', name: "Recipekeeper", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#recipekeeper'},
    {id: 'RECIPESAGE', name: "Recipesage", import: true, export: true, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#recipesage'},
    {id: 'REZKONV', name: "Rezkonv", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#rezkonv'},
    {id: 'SAFFRON', name: "Saffron", import: true, export: true, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#safron'},
    {id: 'REZEPTSUITEDE', name: "Rezeptsuite.de", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#rezeptsuitede'},
    {id: 'GOURMET', name: "Gourmet", import: true, export: false, helpUrl: 'https://github.com/BrendenWalker/TandoorNG/blob/develop/docs/features/import_export.md#gourmet'},
]
