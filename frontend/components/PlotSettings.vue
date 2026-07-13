<template>
    <div class="bg-white rounded-2xl shadow-lg p-6">
        <h2 class="text-lg font-semibold mb-4 flex items-center">
            <i class="fa-solid fa-globe text-indigo-500 mr-2"></i>剧情设置
        </h2>
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">故事背景/世界观</label>
                <textarea v-model="form.background" rows="3" placeholder="描述故事发生的时代、地点、社会背景等" 
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition resize-none"></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">叙事视角</label>
                <select v-model="form.perspective" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none">
                    <option v-for="p in perspectives" :key="p" :value="p">{{p}}</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">冲突类型</label>
                <select v-model="form.conflict" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none">
                    <option v-for="c in conflicts" :key="c" :value="c">{{c}}</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">情感基调</label>
                <select v-model="form.mood" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none">
                    <option v-for="m in moods" :key="m" :value="m">{{m}}</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">故事梗概</label>
                <textarea v-model="form.outline" rows="3" placeholder="简要描述故事的大致情节和走向" 
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition resize-none"></textarea>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'PlotSettings',
    props: {
        form: { type: Object, required: true }
    },
    data() {
        return {
            perspectives: ['第三人称全知', '第三人称有限', '第一人称', '第二人称'],
            conflicts: ['人与自然', '人与社会', '人与人', '内心冲突'],
            moods: ['轻松愉快', '紧张刺激', '温馨感人', '深沉思考', '神秘诡异', '浪漫唯美']
        }
    }
}
</script>
