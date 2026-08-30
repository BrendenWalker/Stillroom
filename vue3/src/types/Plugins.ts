import {RouteRecordRaw} from "vue-router";
import {Component} from "vue";

export type StillroomPlugin = {
    name: string,
    basePath: string,
    defaultLocale: any,
    localeFiles: any,

    routes: RouteRecordRaw[]
    settingRoutes?: RouteRecordRaw[],

    navigationDrawer: any[],
    bottomNavigation: any[],
    userNavigation: any[],

    buildInputs?: string[],

    databasePageComponent?: Component,
    settingsComponent?: Component,

    disabled?: boolean
}

export type PluginModule = {
  plugin: StillroomPlugin
}

const pluginModules = import.meta.glob('@/plugins/*/plugin.ts', { eager: true })
export let STILLROOM_PLUGINS = [] as StillroomPlugin[]
Object.values(pluginModules).forEach(module => {
    if(!module.plugin.disabled){
        STILLROOM_PLUGINS.push(module.plugin)
    }
})