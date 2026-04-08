using System;
using UnityEngine;

/// <summary>
/// 事件管理器
/// 提供全局事件订阅接口（基于 GameEvents 静态类使用）
/// </summary>
public class EventManager : MonoBehaviour
{
    private void OnEnable()
    {
        Debug.Log("[EventManager] 已启用");
    }

    /// <summary>
    /// 全局订阅（便利方法）
    /// </summary>
    public void Subscribe<T>(Action<T> callback) where T : IEventData
    {
        GameEvents.Get<T>().Subscribe(callback);
    }

    /// <summary>
    /// 全局取消订阅
    /// </summary>
    public void Unsubscribe<T>(Action<T> callback) where T : IEventData
    {
        GameEvents.Get<T>().Unsubscribe(callback);
    }
}
