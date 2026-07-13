<template>
    <div class="bg-white rounded-2xl shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold flex items-center">
                <i class="fa-solid fa-lightbulb text-yellow-500 mr-2"></i>伏笔管理
            </h2>
            <button @click="$emit('add')" class="text-sm text-purple-600 hover:text-purple-800 flex items-center gap-1">
                <i class="fa-solid fa-plus"></i>添加伏笔
            </button>
        </div>
        <div v-if="foreshadowings.length === 0" class="border-2 border-dashed border-gray-200 rounded-xl p-4 text-center text-gray-400">
            <i class="fa-solid fa-lightbulb text-3xl mb-2"></i>
            <p>暂无伏笔，点击上方添加</p>
            <p class="text-xs mt-1">伏笔可以是未解开的谜题、隐藏的秘密或未来的线索</p>
        </div>
        <div v-else class="space-y-2">
            <div v-for="(item, index) in foreshadowings" :key="index" 
                class="flex items-center gap-3 bg-gray-50 rounded-lg p-3">
                <input v-model="foreshadowings[index]" type="text" placeholder="输入伏笔内容" 
                    class="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm">
                <button @click="$emit('remove', index)" class="text-red-500 hover:text-red-700">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ForeshadowingManager',
    props: {
        foreshadowings: { type: Array, required: true }
    },
    emits: ['add', 'remove']
}
</script>
