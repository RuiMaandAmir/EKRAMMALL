<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Order;
use App\Models\User;
use App\Models\Product;
use App\Models\Category;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

class StatisticsController extends Controller
{
    /**
     * 获取销售统计数据
     */
    public function sales(Request $request)
    {
        $startDate = $request->input('start_date') ? Carbon::parse($request->input('start_date')) : Carbon::now()->subDays(30);
        $endDate = $request->input('end_date') ? Carbon::parse($request->input('end_date')) : Carbon::now();

        // 计算销售概览数据
        $currentPeriod = Order::whereBetween('created_at', [$startDate, $endDate])
            ->where('status', '!=', 'cancelled')
            ->select(
                DB::raw('SUM(total_amount) as total_amount'),
                DB::raw('COUNT(*) as total_orders'),
                DB::raw('AVG(total_amount) as average_amount'),
                DB::raw('SUM(CASE WHEN status = "refunded" THEN total_amount ELSE 0 END) as refund_amount')
            )->first();

        $previousPeriod = Order::whereBetween('created_at', [
                $startDate->copy()->subDays($endDate->diffInDays($startDate)),
                $startDate
            ])
            ->where('status', '!=', 'cancelled')
            ->select(
                DB::raw('SUM(total_amount) as total_amount'),
                DB::raw('COUNT(*) as total_orders'),
                DB::raw('AVG(total_amount) as average_amount'),
                DB::raw('SUM(CASE WHEN status = "refunded" THEN total_amount ELSE 0 END) as refund_amount')
            )->first();

        // 计算趋势
        $amountTrend = $this->calculateTrend($currentPeriod->total_amount, $previousPeriod->total_amount);
        $ordersTrend = $this->calculateTrend($currentPeriod->total_orders, $previousPeriod->total_orders);
        $averageTrend = $this->calculateTrend($currentPeriod->average_amount, $previousPeriod->average_amount);
        $refundTrend = $this->calculateTrend($currentPeriod->refund_amount, $previousPeriod->refund_amount);

        // 获取销售趋势数据
        $trend = $this->getSalesTrend($startDate, $endDate);

        // 获取商品销售排行
        $productRank = Order::join('order_items', 'orders.id', '=', 'order_items.order_id')
            ->join('products', 'order_items.product_id', '=', 'products.id')
            ->whereBetween('orders.created_at', [$startDate, $endDate])
            ->where('orders.status', '!=', 'cancelled')
            ->select(
                'products.name',
                DB::raw('SUM(order_items.quantity) as sales'),
                DB::raw('SUM(order_items.quantity * order_items.price) as amount')
            )
            ->groupBy('products.id', 'products.name')
            ->orderBy('sales', 'desc')
            ->limit(10)
            ->get();

        // 获取分类销售排行
        $categoryRank = Order::join('order_items', 'orders.id', '=', 'order_items.order_id')
            ->join('products', 'order_items.product_id', '=', 'products.id')
            ->join('categories', 'products.category_id', '=', 'categories.id')
            ->whereBetween('orders.created_at', [$startDate, $endDate])
            ->where('orders.status', '!=', 'cancelled')
            ->select(
                'categories.name',
                DB::raw('SUM(order_items.quantity) as sales'),
                DB::raw('SUM(order_items.quantity * order_items.price) as amount')
            )
            ->groupBy('categories.id', 'categories.name')
            ->orderBy('sales', 'desc')
            ->limit(10)
            ->get();

        return response()->json([
            'total_amount' => round($currentPeriod->total_amount, 2),
            'amount_trend' => $amountTrend,
            'total_orders' => $currentPeriod->total_orders,
            'orders_trend' => $ordersTrend,
            'average_amount' => round($currentPeriod->average_amount, 2),
            'average_trend' => $averageTrend,
            'refund_amount' => round($currentPeriod->refund_amount, 2),
            'refund_trend' => $refundTrend,
            'trend' => $trend,
            'product_rank' => $productRank,
            'category_rank' => $categoryRank
        ]);
    }

    /**
     * 获取用户分析数据
     */
    public function users(Request $request)
    {
        $startDate = $request->input('start_date') ? Carbon::parse($request->input('start_date')) : Carbon::now()->subDays(30);
        $endDate = $request->input('end_date') ? Carbon::parse($request->input('end_date')) : Carbon::now();

        // 计算用户概览数据
        $currentPeriod = User::whereBetween('created_at', [$startDate, $endDate])
            ->select(
                DB::raw('COUNT(*) as new_users'),
                DB::raw('COUNT(DISTINCT CASE WHEN last_login_at >= ? THEN id END) as active_users', [$startDate]),
                DB::raw('COUNT(DISTINCT CASE WHEN EXISTS (
                    SELECT 1 FROM orders WHERE orders.user_id = users.id AND orders.status != "cancelled"
                ) THEN id END) as paid_users')
            )->first();

        $previousPeriod = User::whereBetween('created_at', [
                $startDate->copy()->subDays($endDate->diffInDays($startDate)),
                $startDate
            ])
            ->select(
                DB::raw('COUNT(*) as new_users'),
                DB::raw('COUNT(DISTINCT CASE WHEN last_login_at >= ? THEN id END) as active_users', [$startDate->copy()->subDays($endDate->diffInDays($startDate))]),
                DB::raw('COUNT(DISTINCT CASE WHEN EXISTS (
                    SELECT 1 FROM orders WHERE orders.user_id = users.id AND orders.status != "cancelled"
                ) THEN id END) as paid_users')
            )->first();

        // 计算趋势
        $newUsersTrend = $this->calculateTrend($currentPeriod->new_users, $previousPeriod->new_users);
        $activeUsersTrend = $this->calculateTrend($currentPeriod->active_users, $previousPeriod->active_users);
        $paidUsersTrend = $this->calculateTrend($currentPeriod->paid_users, $previousPeriod->paid_users);

        // 计算留存率
        $retentionRate = $this->calculateRetentionRate($startDate, $endDate);
        $previousRetentionRate = $this->calculateRetentionRate(
            $startDate->copy()->subDays($endDate->diffInDays($startDate)),
            $startDate
        );
        $retentionTrend = $this->calculateTrend($retentionRate, $previousRetentionRate);

        // 获取用户趋势数据
        $trend = $this->getUserTrend($startDate, $endDate);

        // 获取用户地域分布
        $regionDistribution = User::select('province', DB::raw('COUNT(*) as count'))
            ->groupBy('province')
            ->orderBy('count', 'desc')
            ->limit(10)
            ->get()
            ->map(function ($item) {
                return [
                    'name' => $item->province,
                    'value' => $item->count
                ];
            });

        // 获取用户年龄分布
        $ageDistribution = User::select(
                DB::raw('CASE 
                    WHEN age < 18 THEN "18岁以下"
                    WHEN age BETWEEN 18 AND 24 THEN "18-24岁"
                    WHEN age BETWEEN 25 AND 34 THEN "25-34岁"
                    WHEN age BETWEEN 35 AND 44 THEN "35-44岁"
                    WHEN age BETWEEN 45 AND 54 THEN "45-54岁"
                    ELSE "55岁以上"
                END as range'),
                DB::raw('COUNT(*) as count')
            )
            ->groupBy('range')
            ->orderBy('range')
            ->get();

        return response()->json([
            'new_users' => $currentPeriod->new_users,
            'new_users_trend' => $newUsersTrend,
            'active_users' => $currentPeriod->active_users,
            'active_users_trend' => $activeUsersTrend,
            'paid_users' => $currentPeriod->paid_users,
            'paid_users_trend' => $paidUsersTrend,
            'retention_rate' => round($retentionRate, 2),
            'retention_trend' => $retentionTrend,
            'trend' => $trend,
            'region_distribution' => $regionDistribution,
            'age_distribution' => $ageDistribution
        ]);
    }

    /**
     * 获取商品分析数据
     */
    public function products(Request $request)
    {
        $startDate = $request->input('start_date') ? Carbon::parse($request->input('start_date')) : Carbon::now()->subDays(30);
        $endDate = $request->input('end_date') ? Carbon::parse($request->input('end_date')) : Carbon::now();

        // 计算商品概览数据
        $currentPeriod = Product::select(
                DB::raw('COUNT(*) as total_products'),
                DB::raw('COUNT(CASE WHEN status = "on" THEN 1 END) as on_shelf_products'),
                DB::raw('COUNT(CASE WHEN sales_count > 100 THEN 1 END) as hot_products'),
                DB::raw('COUNT(CASE WHEN stock < 10 THEN 1 END) as low_stock_products')
            )->first();

        $previousPeriod = Product::select(
                DB::raw('COUNT(*) as total_products'),
                DB::raw('COUNT(CASE WHEN status = "on" THEN 1 END) as on_shelf_products'),
                DB::raw('COUNT(CASE WHEN sales_count > 100 THEN 1 END) as hot_products'),
                DB::raw('COUNT(CASE WHEN stock < 10 THEN 1 END) as low_stock_products')
            )->first();

        // 计算趋势
        $productsTrend = $this->calculateTrend($currentPeriod->total_products, $previousPeriod->total_products);
        $onShelfTrend = $this->calculateTrend($currentPeriod->on_shelf_products, $previousPeriod->on_shelf_products);
        $hotTrend = $this->calculateTrend($currentPeriod->hot_products, $previousPeriod->hot_products);
        $lowStockTrend = $this->calculateTrend($currentPeriod->low_stock_products, $previousPeriod->low_stock_products);

        // 获取商品趋势数据
        $trend = $this->getProductTrend($startDate, $endDate);

        // 获取分类商品数量分布
        $categoryDistribution = Category::select('name', DB::raw('COUNT(products.id) as count'))
            ->leftJoin('products', 'categories.id', '=', 'products.category_id')
            ->groupBy('categories.id', 'categories.name')
            ->get()
            ->map(function ($item) {
                return [
                    'name' => $item->name,
                    'value' => $item->count
                ];
            });

        // 获取价格区间分布
        $priceDistribution = Product::select(
                DB::raw('CASE 
                    WHEN price < 100 THEN "0-100元"
                    WHEN price BETWEEN 100 AND 500 THEN "100-500元"
                    WHEN price BETWEEN 500 AND 1000 THEN "500-1000元"
                    WHEN price BETWEEN 1000 AND 2000 THEN "1000-2000元"
                    ELSE "2000元以上"
                END as range'),
                DB::raw('COUNT(*) as count')
            )
            ->groupBy('range')
            ->orderBy('range')
            ->get();

        return response()->json([
            'total_products' => $currentPeriod->total_products,
            'products_trend' => $productsTrend,
            'on_shelf_products' => $currentPeriod->on_shelf_products,
            'on_shelf_trend' => $onShelfTrend,
            'hot_products' => $currentPeriod->hot_products,
            'hot_trend' => $hotTrend,
            'low_stock_products' => $currentPeriod->low_stock_products,
            'low_stock_trend' => $lowStockTrend,
            'trend' => $trend,
            'category_distribution' => $categoryDistribution,
            'price_distribution' => $priceDistribution
        ]);
    }

    /**
     * 计算趋势百分比
     */
    private function calculateTrend($current, $previous)
    {
        if ($previous == 0) {
            return $current > 0 ? 100 : 0;
        }
        return round(($current - $previous) / $previous * 100, 2);
    }

    /**
     * 计算用户留存率
     */
    private function calculateRetentionRate($startDate, $endDate)
    {
        $newUsers = User::whereBetween('created_at', [$startDate, $endDate])->count();
        if ($newUsers == 0) {
            return 0;
        }

        $retainedUsers = User::whereBetween('created_at', [$startDate, $endDate])
            ->where('last_login_at', '>=', $endDate->copy()->subDays(7))
            ->count();

        return ($retainedUsers / $newUsers) * 100;
    }

    /**
     * 获取销售趋势数据
     */
    private function getSalesTrend($startDate, $endDate)
    {
        $dates = [];
        $amounts = [];
        $orders = [];

        $current = $startDate->copy();
        while ($current <= $endDate) {
            $dates[] = $current->format('Y-m-d');
            
            $dailyStats = Order::whereDate('created_at', $current)
                ->where('status', '!=', 'cancelled')
                ->select(
                    DB::raw('SUM(total_amount) as amount'),
                    DB::raw('COUNT(*) as orders')
                )->first();

            $amounts[] = round($dailyStats->amount ?? 0, 2);
            $orders[] = $dailyStats->orders ?? 0;

            $current->addDay();
        }

        return [
            'dates' => $dates,
            'amounts' => $amounts,
            'orders' => $orders
        ];
    }

    /**
     * 获取用户趋势数据
     */
    private function getUserTrend($startDate, $endDate)
    {
        $dates = [];
        $newUsers = [];
        $activeUsers = [];
        $paidUsers = [];

        $current = $startDate->copy();
        while ($current <= $endDate) {
            $dates[] = $current->format('Y-m-d');
            
            $dailyStats = User::whereDate('created_at', $current)
                ->select(
                    DB::raw('COUNT(*) as new_users'),
                    DB::raw('COUNT(DISTINCT CASE WHEN last_login_at >= ? THEN id END) as active_users', [$current]),
                    DB::raw('COUNT(DISTINCT CASE WHEN EXISTS (
                        SELECT 1 FROM orders WHERE orders.user_id = users.id AND orders.status != "cancelled"
                    ) THEN id END) as paid_users')
                )->first();

            $newUsers[] = $dailyStats->new_users;
            $activeUsers[] = $dailyStats->active_users;
            $paidUsers[] = $dailyStats->paid_users;

            $current->addDay();
        }

        return [
            'dates' => $dates,
            'new_users' => $newUsers,
            'active_users' => $activeUsers,
            'paid_users' => $paidUsers
        ];
    }

    /**
     * 获取商品趋势数据
     */
    private function getProductTrend($startDate, $endDate)
    {
        $dates = [];
        $totalProducts = [];
        $onShelfProducts = [];
        $hotProducts = [];

        $current = $startDate->copy();
        while ($current <= $endDate) {
            $dates[] = $current->format('Y-m-d');
            
            $dailyStats = Product::whereDate('created_at', '<=', $current)
                ->select(
                    DB::raw('COUNT(*) as total_products'),
                    DB::raw('COUNT(CASE WHEN status = "on" THEN 1 END) as on_shelf_products'),
                    DB::raw('COUNT(CASE WHEN sales_count > 100 THEN 1 END) as hot_products')
                )->first();

            $totalProducts[] = $dailyStats->total_products;
            $onShelfProducts[] = $dailyStats->on_shelf_products;
            $hotProducts[] = $dailyStats->hot_products;

            $current->addDay();
        }

        return [
            'dates' => $dates,
            'total_products' => $totalProducts,
            'on_shelf_products' => $onShelfProducts,
            'hot_products' => $hotProducts
        ];
    }
} 