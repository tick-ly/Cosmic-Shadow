using System;
using System.Collections.Generic;

/// <summary>
/// 泛型事件总线
/// 支持 Subscribe / Unsubscribe / Emit
/// </summary>
public class EventBus<T> where T : IEventData
{
    private readonly List<Action<T>> _listeners = new();
    private readonly List<Action<T>> _pendingAdds = new();
    private readonly List<Action<T>> _pendingRemoves = new();
    private bool _isEmitting = false;

    public void Subscribe(Action<T> callback)
    {
        if (callback == null) return;

        if (_isEmitting)
            _pendingAdds.Add(callback);
        else if (!_listeners.Contains(callback))
            _listeners.Add(callback);
    }

    public void Unsubscribe(Action<T> callback)
    {
        if (callback == null) return;

        if (_isEmitting)
            _pendingRemoves.Add(callback);
        else
            _listeners.Remove(callback);
    }

    public void Emit(T data)
    {
        _isEmitting = true;

        foreach (var listener in _listeners)
        {
            try
            {
                listener?.Invoke(data);
            }
            catch (Exception ex)
            {
                Debug.LogException(ex);
            }
        }

        _isEmitting = false;
        FlushPending();
    }

    private void FlushPending()
    {
        foreach (var add in _pendingAdds)
            if (!_listeners.Contains(add))
                _listeners.Add(add);
        _pendingAdds.Clear();

        foreach (var remove in _pendingRemoves)
            _listeners.Remove(remove);
        _pendingRemoves.Clear();
    }

    public int ListenerCount => _listeners.Count;
}
