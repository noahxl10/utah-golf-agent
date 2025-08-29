import { TestBed } from '@angular/core/testing';

import { TeeTimeService } from './tee-time';

describe('TeeTime', () => {
  let service: TeeTimeService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TeeTimeService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
