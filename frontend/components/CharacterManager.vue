<template>
    <div class="bg-white rounded-2xl shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold flex items-center">
                <i class="fa-solid fa-users text-pink-500 mr-2"></i>角色设定
            </h2>
            <button @click="$emit('openModal')" class="text-sm text-purple-600 hover:text-purple-800 flex items-center gap-1">
                <i class="fa-solid fa-plus"></i>从模板添加
            </button>
        </div>
        <div v-if="characters.length === 0" class="border-2 border-dashed border-gray-200 rounded-xl p-4 text-center text-gray-400">
            <i class="fa-solid fa-users text-3xl mb-2"></i>
            <p>暂无角色，点击上方添加</p>
        </div>
        <div v-else class="space-y-3">
            <div v-for="(char, index) in characters" :key="index" 
                class="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <span class="text-sm font-medium text-gray-700">角色 {{index + 1}}</span>
                        <span v-if="char.is_template" class="text-xs px-2 py-0.5 bg-purple-100 text-purple-600 rounded-full">模板</span>
                    </div>
                    <button @click="$emit('remove', index)" class="text-red-500 hover:text-red-700">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <input v-model="char.name" type="text" placeholder="角色名称" 
                        class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm">
                    <input v-model="char.age" type="text" placeholder="年龄" 
                        class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm">
                </div>
                <div class="grid grid-cols-2 gap-3 mt-2">
                    <input v-model="char.identity" type="text" placeholder="身份" 
                        class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm">
                    <input v-model="char.category" type="text" placeholder="类别" 
                        class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm">
                </div>
                <div class="mt-2">
                    <textarea v-model="char.appearance" rows="2" placeholder="外貌特征" 
                        class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm resize-none"></textarea>
                </div>
                <div class="mt-2">
                    <textarea v-model="char.personality" rows="2" placeholder="性格特点" 
                        class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm resize-none"></textarea>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CharacterManager',
    props: {
        characters: { type: Array, required: true }
    },
    emits: ['openModal', 'remove']
}
</script>
