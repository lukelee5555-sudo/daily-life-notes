---
title: "Ten Smart Home Settings Worth Changing Today"
date: 2026-11-18
summary: "Most smart-home equipment ships with the widest defaults and the thinnest privacy settings. Ten changes, ordered by how much they actually reduce risk."
tags: tech, privacy, home
---

A smart speaker is a microphone with a network connection. A smart plug is a relay that anyone on your network might be able to switch. Neither is a reason to avoid the category — but the factory defaults are chosen so that setup works for everyone, which is the opposite of choosing them for you.

These ten changes take about half an hour. They are ordered by impact, not by how easy they are.

## 1. Give guests and devices their own network

If your router supports a guest network or a separate IoT SSID, put every smart bulb, plug, camera, and TV on it rather than on the network your laptop and phone use. A cheap smart plug that never gets a firmware update becomes a foothold on the guest network instead of on the network where your banking session lives.

Where the router supports VLANs or an "IoT network" toggle, that is the same idea with a cleaner implementation. The point is one hop of separation between devices that get updates and devices that do not.

## 2. Change the default password before anything else

Cameras and hubs with a default admin password are the single most common smart-home compromise. Set a unique password on the device's own web interface, not just in the vendor app, and change the default admin username if the device allows it.

## 3. Turn on two-factor authentication on the vendor account

The device account is the remote control for your home. If it can be logged into from anywhere with only a password, one reused password from an old leak is enough to open your front door camera. Use an authenticator app rather than SMS where both are offered.

## 4. Audit which app has which permission

Voice assistant skills and vendor apps accumulate permissions quietly. Once a month, check which apps can control locks, see cameras, or read your location, and remove anything you cannot explain. On iOS: Settings → Privacy & Security. On Android: Settings → Apps → Special access.

## 5. Set the camera's privacy mask and physical shutter

Almost every indoor camera supports a privacy mask or a "home mode" that stops recording when you are home. Use it, and prefer cameras with a physical shutter over a software toggle — the shutter cannot be defeated by a firmware bug.

Change the default stream password too, and never expose a camera directly to the internet through port forwarding. Use the vendor's cloud relay or a VPN into your own network.

## 6. Disable the features you are not using

Remote access you never set up, cloud recording you do not pay for, "share with friends" links, voice purchasing, and routine suggestions are all attack surface with no upside if you do not use them. Vendor apps hide these in per-device settings rather than account settings, so check both.

## 7. Put the hub on a scheduled reboot and check firmware monthly

Unpatched firmware is the most common route in. Turn on automatic updates where the vendor offers them, and where it does not, put a recurring reminder in your calendar — monthly is enough for most gear. A hub that has been up for 400 days is usually also a hub that has not been patched in 400 days.

## 8. Name devices for what they are, not where they are

"Bedroom camera" tells a support agent, a housemate, and anyone who gets into the account exactly what is in that room. A neutral name like "Cam 3" does the same job for you and less for everyone else. The same applies to the Wi-Fi SSID: a network called "Kim-family-3F" is a social-engineering aid.

## 9. Review the data retention settings

Many vendors keep voice recordings and camera clips for 30 to 180 days by default, and some keep a transcript indefinitely. Turn on deletion after review, disable "help improve our service" audio donation, and delete the recordings you have already listened to. This is the setting that most often surprises people during a breach notification.

## 10. Write down what you own, and where the reset is

A one-page list — device, vendor account email, where the physical reset button is, and what the device controls — turns a lost phone or a dead hub into a fifteen-minute fix instead of an evening of guessing. Store it somewhere that is not the device itself.

## The ten-minute version

If you only do three things: separate the IoT network, set non-default admin passwords, and turn on two-factor on every vendor account. Those three close the routes that account for most real-world incidents.

## One honest caveat

Smart home gear is a trade: convenience in exchange for a device that is always on your network and always talking to someone's cloud. If a device's only benefit is turning a light on by voice, a five-dollar mechanical timer does the same job with no account, no firmware, and no breach history. Deciding not to connect something is a legitimate setting too.
