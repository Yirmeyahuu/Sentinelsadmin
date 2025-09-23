// Help content configuration
    window.helpContentMap = {
        '/Superadmin/homepage/': {
            title: 'Dashboard Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-2xl border-l-4 border-blue-500">
                        <h4 class="font-bold text-blue-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                            </svg>
                            Dashboard Overview
                        </h4>
                        <p class="text-gray-700 leading-relaxed">This dashboard provides a comprehensive overview of your system with real-time statistics and insights.</p>
                    </div>
                    
                    <div class="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-2xl border-l-4 border-green-500">
                        <h4 class="font-bold text-green-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Statistics Cards
                        </h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div class="flex items-center">
                                    <div class="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Total Students:</span>
                                        <p class="text-sm text-gray-600 mt-1">Shows the total number of registered students</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div class="flex items-center">
                                    <div class="w-3 h-3 bg-indigo-500 rounded-full mr-3"></div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Total Faculty:</span>
                                        <p class="text-sm text-gray-600 mt-1">Displays the number of active faculty members</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div class="flex items-center">
                                    <div class="w-3 h-3 bg-amber-500 rounded-full mr-3"></div>
                                    <div>
                                        <span class="font-semibold text-gray-800">CS Students:</span>
                                        <p class="text-sm text-gray-600 mt-1">Computer Science program student count</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div class="flex items-center">
                                    <div class="w-3 h-3 bg-rose-500 rounded-full mr-3"></div>
                                    <div>
                                        <span class="font-semibold text-gray-800">IT Students:</span>
                                        <p class="text-sm text-gray-600 mt-1">Information Technology program student count</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-purple-50 to-violet-50 p-6 rounded-2xl border-l-4 border-purple-500">
                        <h4 class="font-bold text-purple-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                                <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                            </svg>
                            Activity Progress Chart
                        </h4>
                        <p class="text-gray-700 leading-relaxed">Track student progress across different activity tiers. Use the dropdown to filter by program and view detailed analytics.</p>
                    </div>
                </div>
            `
        },
        '/Superadmin/Activity-list/': {
            title: 'Activities Management Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-cyan-50 to-blue-50 p-6 rounded-2xl border-l-4 border-cyan-500">
                        <h4 class="font-bold text-cyan-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                            </svg>
                            Activity Tiers
                        </h4>
                        <div class="space-y-3">
                            <div class="flex items-center p-3 bg-white rounded-xl shadow-sm border border-gray-100">
                                <div class="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center font-bold text-sm mr-4">N</div>
                                <div>
                                    <span class="font-semibold text-gray-800">Novice:</span>
                                    <span class="text-gray-600 ml-2">Entry-level activities for beginners</span>
                                </div>
                            </div>
                            <div class="flex items-center p-3 bg-white rounded-xl shadow-sm border border-gray-100">
                                <div class="w-8 h-8 bg-yellow-100 text-yellow-600 rounded-full flex items-center justify-center font-bold text-sm mr-4">J</div>
                                <div>
                                    <span class="font-semibold text-gray-800">Junior:</span>
                                    <span class="text-gray-600 ml-2">Intermediate activities</span>
                                </div>
                            </div>
                            <div class="flex items-center p-3 bg-white rounded-xl shadow-sm border border-gray-100">
                                <div class="w-8 h-8 bg-red-100 text-red-600 rounded-full flex items-center justify-center font-bold text-sm mr-4">S</div>
                                <div>
                                    <span class="font-semibold text-gray-800">Senior:</span>
                                    <span class="text-gray-600 ml-2">Advanced activities for experienced users</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-orange-50 to-amber-50 p-6 rounded-2xl border-l-4 border-orange-500">
                        <h4 class="font-bold text-orange-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                            </svg>
                            Tier Controls
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">Use the <span class="px-2 py-1 bg-green-100 text-green-700 rounded-md font-medium">Activate</span> / <span class="px-2 py-1 bg-red-100 text-red-700 rounded-md font-medium">Deactivate</span> buttons to control access to each tier level.</p>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-teal-50 to-cyan-50 p-6 rounded-2xl border-l-4 border-teal-500">
                        <h4 class="font-bold text-teal-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                            </svg>
                            Activity Cards
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">Click on any activity card to view detailed information. Locked activities are indicated by a <span class="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded-md font-medium"><svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" /></svg>lock icon</span>.</p>
                        </div>
                    </div>
                </div>
            `
        },
        '/Superadmin/Faculty-list/': {
            title: 'Faculty List Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-2xl border-l-4 border-indigo-500">
                        <h4 class="font-bold text-indigo-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM9 14a6 6 0 00-6 6h12a6 6 0 00-6-6z" />
                            </svg>
                            Faculty Management
                        </h4>
                        <p class="text-gray-700 leading-relaxed">This page allows you to manage all registered faculty members with comprehensive tools for administration.</p>
                    </div>
                    
                    <div class="bg-gradient-to-r from-emerald-50 to-teal-50 p-6 rounded-2xl border-l-4 border-emerald-500">
                        <h4 class="font-bold text-emerald-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                            </svg>
                            Available Actions
                        </h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Search</span>
                                        <p class="text-sm text-gray-600 mt-1">Find specific faculty members</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Add Faculty</span>
                                        <p class="text-sm text-gray-600 mt-1">Register new faculty members</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-yellow-100 text-yellow-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Edit</span>
                                        <p class="text-sm text-gray-600 mt-1">Modify faculty information</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Move</span>
                                        <p class="text-sm text-gray-600 mt-1">Change faculty status or location</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-pink-50 to-rose-50 p-6 rounded-2xl border-l-4 border-pink-500">
                        <h4 class="font-bold text-pink-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clip-rule="evenodd" />
                            </svg>
                            Status Indicators
                        </h4>
                        <div class="flex flex-wrap gap-3">
                            <div class="flex items-center px-3 py-2 bg-green-100 text-green-700 rounded-full">
                                <div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                                <span class="font-medium">Active</span>
                            </div>
                            <div class="flex items-center px-3 py-2 bg-yellow-100 text-yellow-700 rounded-full">
                                <div class="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                                <span class="font-medium">Completed</span>
                            </div>
                            <div class="flex items-center px-3 py-2 bg-red-100 text-red-700 rounded-full">
                                <div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                                <span class="font-medium">Deactivated</span>
                            </div>
                        </div>
                    </div>
                </div>
            `
        },
        '/Superadmin/Faculty-status/': {
            title: 'Faculty Status Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-blue-50 to-cyan-50 p-6 rounded-2xl border-l-4 border-blue-500">
                        <h4 class="font-bold text-blue-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd" />
                            </svg>
                            Status Filtering
                        </h4>
                        <p class="text-gray-700 leading-relaxed">Filter faculty by status, program, year & section, and semester to find exactly what you're looking for.</p>
                    </div>
                    
                    <div class="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-2xl border-l-4 border-green-500">
                        <h4 class="font-bold text-green-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                            </svg>
                            Status Types
                        </h4>
                        <div class="space-y-3">
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-green-100 text-green-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800 text-base">Continuing</span>
                                        <p class="text-gray-600 text-sm">Currently active faculty members</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-yellow-100 text-yellow-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800 text-base">Completed</span>
                                        <p class="text-gray-600 text-sm">Faculty who have finished their term</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-red-100 text-red-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800 text-base">Deactivated</span>
                                        <p class="text-gray-600 text-sm">Inactive faculty accounts</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-2xl border-l-4 border-purple-500">
                        <h4 class="font-bold text-purple-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
                            </svg>
                            Quick Actions
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">Use the <span class="inline-flex items-center px-2 py-1 bg-purple-100 text-purple-700 rounded-md font-medium"><svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>move button</span> to quickly change a faculty member's status.</p>
                        </div>
                    </div>
                </div>
            `
        },
        '/Superadmin/Faculty-Archived/': {
            title: 'Archived Faculty Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-gray-50 to-slate-50 p-6 rounded-2xl border-l-4 border-gray-500">
                        <h4 class="font-bold text-gray-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z" />
                                <path fill-rule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clip-rule="evenodd" />
                            </svg>
                            Archived Faculty
                        </h4>
                        <p class="text-gray-700 leading-relaxed">This section contains faculty members who have been archived (deactivated). Archived records are preserved for historical purposes.</p>
                    </div>
                    
                    <div class="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-2xl border-l-4 border-orange-500">
                        <h4 class="font-bold text-orange-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                            </svg>
                            Available Actions
                        </h4>
                        <div class="space-y-3">
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Search</span>
                                        <p class="text-gray-600 text-sm">Find specific archived faculty members</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-green-100 text-green-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Restore</span>
                                        <p class="text-gray-600 text-sm">Restore faculty to active status</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow border-red-200">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-red-100 text-red-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clip-rule="evenodd" /><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-red-700">Delete</span>
                                        <p class="text-red-600 text-sm">Permanently remove faculty records <span class="font-medium">(use with caution)</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-indigo-50 to-blue-50 p-6 rounded-2xl border-l-4 border-indigo-500">
                        <h4 class="font-bold text-indigo-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                            </svg>
                            Archive Information
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">The <span class="font-medium text-indigo-600">"Archived On"</span> column shows when the faculty was deactivated, providing a complete audit trail.</p>
                        </div>
                    </div>
                </div>
            `
        },

        '/Superadmin/Student-list/': {
            title: 'Student List Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-2xl border-l-4 border-indigo-500">
                        <h4 class="font-bold text-indigo-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12a1 1 0 001-1v-3a1 1 0 00-1-1H8a1 1 0 00-1 1v3a1 1 0 001 1h1zM9 15a1 1 0 001-1v-1a1 1 0 00-1-1H8a1 1 0 00-1 1v1a1 1 0 001 1h1z" />
                                <path fill-rule="evenodd" d="M4.293 2.293A1 1 0 017 2h6a1 1 0 01.707.293l3 3A1 1 0 0117 6v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1h2.293zM7 4v2a1 1 0 001 1h2a1 1 0 001-1V4h4v9H4V4h3z" clip-rule="evenodd" />
                            </svg>
                            Student Management
                        </h4>
                        <p class="text-gray-700 leading-relaxed">This page allows you to manage all registered students with comprehensive tools for administration and monitoring.</p>
                    </div>
                    
                    <div class="bg-gradient-to-r from-emerald-50 to-teal-50 p-6 rounded-2xl border-l-4 border-emerald-500">
                        <h4 class="font-bold text-emerald-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                            </svg>
                            Available Actions
                        </h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Search</span>
                                        <p class="text-sm text-gray-600 mt-1">Find specific students by name or ID</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Add Student</span>
                                        <p class="text-sm text-gray-600 mt-1">Register new students</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-yellow-100 text-yellow-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Edit</span>
                                        <p class="text-sm text-gray-600 mt-1">Modify student information</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center mr-3">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Move</span>
                                        <p class="text-sm text-gray-600 mt-1">Change student status or section</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-pink-50 to-rose-50 p-6 rounded-2xl border-l-4 border-pink-500">
                        <h4 class="font-bold text-pink-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clip-rule="evenodd" />
                            </svg>
                            Student Information
                        </h4>
                        <div class="space-y-3">
                            <div class="bg-white p-3 rounded-xl shadow-sm border border-gray-100">
                                <span class="font-medium text-gray-800">Student ID:</span>
                                <span class="text-gray-600 ml-2">Unique identifier for each student</span>
                            </div>
                            <div class="bg-white p-3 rounded-xl shadow-sm border border-gray-100">
                                <span class="font-medium text-gray-800">Program:</span>
                                <span class="text-gray-600 ml-2">Computer Science (CS) or Information Technology (IT)</span>
                            </div>
                            <div class="bg-white p-3 rounded-xl shadow-sm border border-gray-100">
                                <span class="font-medium text-gray-800">Year & Section:</span>
                                <span class="text-gray-600 ml-2">Academic year level and class section</span>
                            </div>
                        </div>
                    </div>
                </div>
            `
        },

        '/Superadmin/Student-status/': {
            title: 'Student Status Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-blue-50 to-cyan-50 p-6 rounded-2xl border-l-4 border-blue-500">
                        <h4 class="font-bold text-blue-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd" />
                            </svg>
                            Status Filtering
                        </h4>
                        <p class="text-gray-700 leading-relaxed">Filter students by status, program, year & section, and semester to track student progress and manage enrollments effectively.</p>
                    </div>
                    
                    <div class="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-2xl border-l-4 border-green-500">
                        <h4 class="font-bold text-green-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                            </svg>
                            Student Status Types
                        </h4>
                        <div class="space-y-3">
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-green-100 text-green-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800 text-base">Continuing</span>
                                        <p class="text-gray-600 text-sm">Currently enrolled and active students</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-yellow-100 text-yellow-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800 text-base">Completed</span>
                                        <p class="text-gray-600 text-sm">Students who have graduated or finished their program</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-red-100 text-red-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800 text-base">Deactivated</span>
                                        <p class="text-gray-600 text-sm">Inactive student accounts (dropped out, suspended, etc.)</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-2xl border-l-4 border-purple-500">
                        <h4 class="font-bold text-purple-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
                            </svg>
                            Quick Actions
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">Use the <span class="inline-flex items-center px-2 py-1 bg-purple-100 text-purple-700 rounded-md font-medium"><svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>move button</span> to quickly change a student's status or transfer them between sections.</p>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-amber-50 to-orange-50 p-6 rounded-2xl border-l-4 border-amber-500">
                        <h4 class="font-bold text-amber-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                            Academic Progress Tracking
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">Monitor student progress through different tiers of activities and track their academic journey from enrollment to graduation.</p>
                        </div>
                    </div>
                </div>
            `
        },

        '/Superadmin/Student-Archived/': {
            title: 'Archived Students Help',
            content: `
                <div class="space-y-6">
                    <div class="bg-gradient-to-r from-gray-50 to-slate-50 p-6 rounded-2xl border-l-4 border-gray-500">
                        <h4 class="font-bold text-gray-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z" />
                                <path fill-rule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clip-rule="evenodd" />
                            </svg>
                            Archived Students
                        </h4>
                        <p class="text-gray-700 leading-relaxed">This section contains students who have been archived (deactivated). This includes students who have dropped out, been suspended, or otherwise left the program. Archived records are preserved for historical and administrative purposes.</p>
                    </div>
                    
                    <div class="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-2xl border-l-4 border-orange-500">
                        <h4 class="font-bold text-orange-700 mb-4 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                            </svg>
                            Available Actions
                        </h4>
                        <div class="space-y-3">
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Search</span>
                                        <p class="text-gray-600 text-sm">Find specific archived students by name or student ID</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-green-100 text-green-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-gray-800">Restore</span>
                                        <p class="text-gray-600 text-sm">Restore student to active status (re-enrollment)</p>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow border-red-200">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 bg-red-100 text-red-600 rounded-full flex items-center justify-center mr-4">
                                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clip-rule="evenodd" /><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>
                                    </div>
                                    <div>
                                        <span class="font-semibold text-red-700">Delete</span>
                                        <p class="text-red-600 text-sm">Permanently remove student records <span class="font-medium">(use with extreme caution)</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-indigo-50 to-blue-50 p-6 rounded-2xl border-l-4 border-indigo-500">
                        <h4 class="font-bold text-indigo-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                            </svg>
                            Archive Information
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">The <span class="font-medium text-indigo-600">"Archived On"</span> column shows when the student was deactivated. This provides a complete audit trail and helps track when students left the program.</p>
                        </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-yellow-50 to-amber-50 p-6 rounded-2xl border-l-4 border-yellow-500">
                        <h4 class="font-bold text-yellow-700 mb-3 flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                            Important Note
                        </h4>
                        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-700 leading-relaxed">Archived students retain their academic history and progress data. Use the restore function to re-enroll students who wish to return to the program.</p>
                        </div>
                    </div>
                </div>
            `
        }
    };

// Initialize tooltip when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.initTooltip) {
        window.initTooltip();
    }
});
    
// Reinitialize tooltip after HTMX content swaps
document.addEventListener('htmx:afterSwap', function() {
    if (window.initTooltip) {
        window.initTooltip();
    }
});


    // Tooltip/Help Feature
window.initTooltip = function() {
    // Remove existing tooltip if any
    const existingTooltip = document.getElementById('helpTooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }

    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.id = 'helpTooltip';
    tooltip.className = 'fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full shadow-lg cursor-pointer transition-all duration-300 hover:scale-105 z-50';
    tooltip.innerHTML = `
        <div class="flex items-center space-x-2 group">
            <svg class="w-4 h-4 transition-transform group-hover:scale-110" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
            </svg>
            <span class="text-sm font-medium">Need Help?</span>
        </div>
    `;

    // Get current page context
    const currentUrl = window.location.pathname;
    let helpContent = getHelpContent(currentUrl);

    // Add click event
    tooltip.addEventListener('click', function() {
        showHelpModal(helpContent);
    });

    // Append to body
    document.body.appendChild(tooltip);
};

function getHelpContent(url) {
    // Use the global help content map defined in the HTML
    const helpMap = window.helpContentMap || {};
    
    return helpMap[url] || {
        title: 'Help',
        content: '<p class="text-gray-700">Help information for this page is not available.</p>'
    };
}

function showHelpModal(helpContent) {
    // Remove existing modal if any
    const existingModal = document.getElementById('helpModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'helpModal';
    modal.className = 'fixed inset-0 flex items-center justify-center bg-gray-900/80 z-[9999]';
    modal.innerHTML = `
            <div class="prose prose-sm max-w-none">
                ${helpContent.content}
            </div>
            <div class="flex justify-end mt-6 pt-4 border-t border-gray-200">
                <button onclick="closeHelpModal()" 
                        class="bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 transition-colors">
                    Got it!
                </button>
            </div>
    `;

    // Add click outside to close
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeHelpModal();
        }
    });

    document.body.appendChild(modal);
}

window.closeHelpModal = function() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        modal.remove();
    }
};

// Auto-initialize tooltip when page loads
document.addEventListener('DOMContentLoaded', function() {
    initTooltip();
});

// Reinitialize tooltip after HTMX swaps
document.addEventListener('htmx:afterSwap', function() {
    initTooltip();
});

function showHelpModal(helpContent) {
    // Remove existing modal if any
    const existingModal = document.getElementById('helpModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'helpModal';
    modal.className = 'fixed inset-0 flex items-center justify-center backdrop-blur-xs bg-gray-900/80 z-[9999]';
    modal.innerHTML = `
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[80vh] border-2 backdrop-blur-xs border-blue-500/20 flex flex-col">
            <!-- Fixed Header with Close Button -->
            <div class="flex justify-between items-center p-8 pb-4 border-b border-gray-200 flex-shrink-0">
                <h2 class="text-2xl font-bold text-blue-600">${helpContent.title}</h2>
                <button onclick="closeHelpModal()" class="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            
            <!-- Scrollable Content Area -->
            <div class="flex-1 overflow-y-auto px-8 py-4">
                <div class="prose prose-sm max-w-none">
                    ${helpContent.content}
                </div>
            </div>
            
            <!-- Fixed Footer with Button -->
            <div class="flex justify-end p-8 pt-4 border-t border-gray-200 flex-shrink-0">
                <button onclick="closeHelpModal()" 
                        class="bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 transition-colors">
                    Got it!
                </button>
            </div>
        </div>
    `;

    // Add click outside to close
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeHelpModal();
        }
    });

    document.body.appendChild(modal);
}

window.closeHelpModal = function() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        modal.remove();
    }
};

// Auto-initialize tooltip when page loads
document.addEventListener('DOMContentLoaded', function() {
    initTooltip();
});

// Reinitialize tooltip after HTMX swaps
document.addEventListener('htmx:afterSwap', function() {
    // Small delay to ensure URL has updated
    setTimeout(() => {
        initTooltip();
    }, 100);
});