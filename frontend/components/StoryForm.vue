<template>
    <div class="bg-white rounded-2xl shadow-lg p-6">
        <h2 class="text-lg font-semibold mb-4 flex items-center">
            <i class="fa-solid fa-pencil text-purple-500 mr-2"></i>基本信息
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">故事主题</label>
                <input v-model="form.theme" type="text" placeholder="输入故事主题" 
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">体裁</label>
                <select v-model="form.genre" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none">
                    <option v-for="g in genres" :key="g" :value="g">{{g}}</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">风格</label>
                <select v-model="form.style" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none">
                    <option v-for="s in styles" :key="s" :value="s">{{s}}</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">目标字数</label>
                <input v-model.number="form.length" type="range" min="500" max="5000" step="500"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600">
                <div class="text-center text-sm text-gray-500">{{form.length}} 字</div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'StoryForm',
    props: {
        form: { type: Object, required: true }
    },
    data() {
        return {
            genres: ['短篇小说', '中篇小说', '日常小短文', '散文', '剧本', '童话', '诗歌', '悬疑推理', '科幻', '奇幻'],
            styles: ['温馨', '悬疑', '科幻', '古风', '奇幻', '幽默', '伤感', '浪漫', '史诗', '治愈']
        }
    }
}
</script>
