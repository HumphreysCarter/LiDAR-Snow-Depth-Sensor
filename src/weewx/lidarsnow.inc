<div id='lidarsnow_widget' class="widget">
  <div class="widget_title">
    <a href="lidarsnow.html">LiDAR Snow Data</a>
    <a class="widget_control"
      onclick="toggle_widget('lidarsnow')">&diams;</a>
  </div>

  <div class="widget_contents">
  <table>
    <tbody>
      <tr>
        <td class="label">$obs.label.lidar_distance</td>
        <td class="data">$current.lidar_distance.format(format_string="%.1f")</td>
      </tr>
      <tr>
        <td class="label">$obs.label.lidar_snowdepth</td>
        <td class="data">$current.lidar_snowdepth.format(format_string="%.1f")</td>
      </tr>
      <tr>
        <td class="label">$obs.label.lidar_snowfall</td>
        <td class="data">$current.lidar_snowfall.format(format_string="%.1f")</td>
      </tr>
      <tr>
        <td class="label">$obs.label.lidar_boardtemp</td>
        <td class="data">$current.lidar_boardtemp</td>
     </tr>
    </tbody>
  </table>
  </div>
</div>
