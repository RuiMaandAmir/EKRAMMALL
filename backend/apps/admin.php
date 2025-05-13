// 数据统计路由
Route::prefix('statistics')->group(function () {
    Route::get('/sales', [StatisticsController::class, 'sales']);
    Route::get('/users', [StatisticsController::class, 'users']);
    Route::get('/products', [StatisticsController::class, 'products']);
}); 