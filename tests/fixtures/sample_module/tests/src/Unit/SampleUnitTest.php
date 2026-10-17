<?php

declare(strict_types=1);

namespace Drupal\Tests\sample_module\Unit;

use PHPUnit\Framework\TestCase;

/**
 * Tests sample SRE module calculations.
 *
 * @group sample_module
 */
final class SampleUnitTest extends TestCase {

  /**
   * Tests latency threshold evaluator.
   */
  public function testLatencyThreshold(): void {
    $threshold = 500;
    $observed = 320;

    $this->assertLessThanOrEqual($threshold, $observed, 'Observed latency must stay within SLO budget.');
  }

  /**
   * Tests error budget remaining calculation.
   */
  public function testErrorBudgetCalculation(): void {
    $totalRequests = 100000;
    $failedRequests = 25;
    // 99.9% availability target.
    $sloTarget = 0.999;

    $availability = ($totalRequests - $failedRequests) / $totalRequests;

    $this->assertGreaterThanOrEqual($sloTarget, $availability, 'Availability SLO target must be met.');
  }

}
