# ResourcePacksInfoPacket

__ID: 6__



<table><thead><tr><th>Field</th><th>Info</th></tr></thead><tbody>
<tr><td>Resource Pack Required</td><td>bool</td></tr>
<tr><td>Has Add-on Packs</td><td>bool</td></tr>
<tr><td>Has Scripts</td><td>bool</td></tr>
<tr><td>Resource Packs</td><td><b>Resource Pack Count:</b> unsigned short
  <table><thead><tr><th>Field</th><th>Info</th></tr></thead><tbody>
  <tr><td>ID</td><td>string</td></tr>
  <tr><td>Version</td><td>string</td></tr>
  <tr><td>Size</td><td>unsigned int64</td></tr>
  <tr><td>Content Key</td><td>string</td></tr>
  <tr><td>Sub Pack Name</td><td>string</td></tr>
  <tr><td>Content Identity</td><td>string</td></tr>
  <tr><td>Has Scripts</td><td>bool</td></tr>
  <tr><td>Is Addon Pack</td><td><table><tbody><tr><td>bool</td><td>Indicates this pack is part of an Add-On. Helps clients determine if the pack must be downloaded to join the server as Add-On packs are required to play without issues.</td></tr></tbody></table></td></tr>
  <tr><td>Is Ray Tracing Capable</td><td>bool</td></tr>
  <tr><td>CDN URL</td><td>string</td></tr>
  </tbody></table></td></tr>
</tbody></table>