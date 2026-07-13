<template>
    <div class="bg-white rounded-2xl shadow-lg p-6">
        <h2 class="text-lg font-semibold mb-4 flex items-center">
            <i class="fa-solid fa-book-open text-cyan-500 mr-2"></i>世界观设定
        </h2>
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">世界背景</label>
                <textarea v-model="form.world_setting" rows="4" placeholder="详细描述故事所处的世界，包括地理、种族、魔法体系、历史背景等..." 
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition resize-none"></textarea>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'WorldSetting',
    props: {
        form: { type: Object, required: true }
    }
}
</script>
