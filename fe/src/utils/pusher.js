import Pusher from 'pusher-js';

let pusherInstance = null;

export const initPusher = (key, cluster) => {
  if (!pusherInstance) {
    pusherInstance = new Pusher(key, { cluster });
  }
  return pusherInstance;
};

export const subscribeToChannel = (channelName, eventName, callback) => {
  if (!pusherInstance) {
    throw new Error('Pusher not initialized. Call initPusher first.');
  }

  const channel = pusherInstance.subscribe(channelName);
  channel.bind(eventName, callback);

  return () => {
    channel.unbind(eventName);
    pusherInstance.unsubscribe(channelName);
  };
};

export const disconnectPusher = () => {
  if (pusherInstance) {
    pusherInstance.disconnect();
  }
};
